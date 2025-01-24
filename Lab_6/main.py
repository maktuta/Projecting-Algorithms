import tkinter as tk
import random
from copy import deepcopy
import time

# Вузли та лінії для початкової конфігурації
def create_initial_graph():
    return {
        'nodes': ['Head', 'Body', 'LeftArm', 'RightArm', 'LeftLeg', 'RightLeg', 'Ground1', 'Ground2'],
        'edges': [
            ('Head', 'Body'), ('Body', 'LeftArm'), ('Body', 'RightArm'),
            ('Body', 'LeftLeg'), ('Body', 'RightLeg'),
            ('LeftLeg', 'Ground1'), ('RightLeg', 'Ground2')
        ],
        'ground': ['Ground1', 'Ground2']  # Вузли, що торкаються землі
    }

class HackenbushGame:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=600, height=400, bg="white")
        self.canvas.pack()
        self.graph = create_initial_graph()
        self.difficulty = "hard"
        self.current_player = "User"
        self.last_player = None
        self.winner = None
        self.draw_graph()
        self.canvas.bind("<Button-1>", self.handle_click)

    def draw_graph(self):
        self.canvas.delete("all")
        self.positions = {
            'Head': (300, 100), 'Body': (300, 200),
            'LeftArm': (200, 200), 'RightArm': (400, 200),
            'LeftLeg': (250, 300), 'RightLeg': (350, 300),
            'Ground1': (250, 350), 'Ground2': (350, 350)
        }
        # Малюємо землю
        self.canvas.create_line(200, 360, 400, 360, width=2, fill="gray", dash=(5, 2))
        # Малюємо ребра
        for edge in self.graph['edges']:
            x1, y1 = self.positions[edge[0]]
            x2, y2 = self.positions[edge[1]]
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill="black", tags=f"edge-{edge[0]}-{edge[1]}")
        # Малюємо вузли
        for node, pos in self.positions.items():
            x, y = pos
            color = "green" if node in self.graph['ground'] else "black"
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color)

    def handle_click(self, event):
        if self.winner is not None:
            return

        x, y = event.x, event.y
        for edge in self.graph['edges']:
            x1, y1 = self.positions[edge[0]]
            x2, y2 = self.positions[edge[1]]
            if self.is_near_line(x, y, x1, y1, x2, y2):
                self.highlight_edge(edge, "blue")
                self.master.update()
                time.sleep(0.5)
                self.graph['edges'].remove(edge)
                self.last_player = "User"
                self.remove_unattached_parts()
                self.draw_graph()
                if not self.check_game_over():
                    self.current_player = "Computer"
                    self.computer_move()
                return

    def highlight_edge(self, edge, color):
        x1, y1 = self.positions[edge[0]]
        x2, y2 = self.positions[edge[1]]
        self.canvas.create_line(x1, y1, x2, y2, width=2, fill=color)

    def is_near_line(self, x, y, x1, y1, x2, y2):
        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return distance < 10

    def computer_move(self):
        if self.winner is not None:
            return

        if self.difficulty == "easy":
            move = random.choice(self.graph['edges'])
        elif self.difficulty == "medium":
            move = self.best_move(depth=2)
        elif self.difficulty == "hard":
            move = self.best_move(depth=7)

        if move:
            self.highlight_edge(move, "red")
            self.master.update()
            time.sleep(0.5)
            self.graph['edges'].remove(move)
            self.last_player = "Computer"
            self.remove_unattached_parts()
            self.draw_graph()
            self.check_game_over()
            self.current_player = "User"

    def remove_unattached_parts(self):
        connected = set(self.graph['ground'])
        edges = self.graph['edges']
        while True:
            new_connected = connected.copy()
            for edge in edges:
                if edge[0] in connected or edge[1] in connected:
                    new_connected.update(edge)
            if new_connected == connected:
                break
            connected = new_connected

        self.graph['edges'] = [edge for edge in edges if edge[0] in connected and edge[1] in connected]
        self.graph['nodes'] = [node for node in self.graph['nodes'] if node in connected]

    def best_move(self, depth):
        moves = self.graph['edges']
        best_score = float('-inf')
        best_move = None

        for move in moves:
            new_graph = deepcopy(self.graph)
            new_graph['edges'].remove(move)
            self.simulate_remove_unattached_parts(new_graph)
            score = self.minimax(new_graph, depth - 1, False, float('-inf'), float('inf'))
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def simulate_remove_unattached_parts(self, graph):
        connected = set(graph['ground'])
        edges = graph['edges']
        while True:
            new_connected = connected.copy()
            for edge in edges:
                if edge[0] in connected or edge[1] in connected:
                    new_connected.update(edge)
            if new_connected == connected:
                break
            connected = new_connected

        graph['edges'] = [edge for edge in edges if edge[0] in connected and edge[1] in connected]
        graph['nodes'] = [node for node in graph['nodes'] if node in connected]

    def minimax(self, graph, depth, maximizing_player, alpha, beta):
        if depth == 0 or not graph['edges']:
            return self.evaluate(graph)

        if maximizing_player:
            max_eval = float('-inf')
            for move in graph['edges']:
                new_graph = deepcopy(graph)
                new_graph['edges'].remove(move)
                self.simulate_remove_unattached_parts(new_graph)
                eval = self.minimax(new_graph, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in graph['edges']:
                new_graph = deepcopy(graph)
                new_graph['edges'].remove(move)
                self.simulate_remove_unattached_parts(new_graph)
                eval = self.minimax(new_graph, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self, graph):
        return len(graph['edges'])

    def check_game_over(self):
        if not self.graph['edges']:
            self.winner = self.last_player
            self.canvas.create_text(300, 200, text=f"Game Over! {self.winner} wins!", font=("Arial", 24), fill="red")
            return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hackenbush Game")
    game = HackenbushGame(root)
    root.mainloop()
