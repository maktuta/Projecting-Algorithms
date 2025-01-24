import numpy as np
import random
import time


class BeeAlgorithm:
    def __init__(self, distance_matrix, num_areas, num_foragers, num_scouts, max_iterations):
        self.distance_matrix = distance_matrix
        self.num_cities = len(distance_matrix)
        self.num_areas = num_areas
        self.num_foragers = num_foragers
        self.num_scouts = num_scouts
        self.max_iterations = max_iterations
        self.execution_time = 0

    def calculate_route_distance(self, route):
        """Обчислює довжину маршруту."""
        return sum(self.distance_matrix[route[i - 1], route[i]] for i in range(len(route)))

    def random_route(self):
        """Генерує випадковий маршрут."""
        route = list(range(self.num_cities))
        random.shuffle(route)
        return route

    def neighborhood_search(self, route):
        """Пошук у околі: перестановка двох міст у маршруті."""
        new_route = route[:]
        i, j = random.sample(range(len(route)), 2)
        new_route[i], new_route[j] = new_route[j], new_route[i]
        return new_route

    def initialize_population(self):
        """Ініціалізує популяцію ділянок."""
        return [self.random_route() for _ in range(self.num_areas)]

    def run(self):
        """Основний цикл алгоритму."""
        start_time = time.time()

        # Ініціалізація ділянок
        areas = self.initialize_population()
        best_route = None
        best_distance = float('inf')

        for iteration in range(self.max_iterations):
            new_areas = []

            # Фуражири обстежують ділянки
            for area in areas:
                for _ in range(self.num_foragers):
                    candidate_route = self.neighborhood_search(area)
                    candidate_distance = self.calculate_route_distance(candidate_route)
                    if candidate_distance < self.calculate_route_distance(area):
                        area = candidate_route
                new_areas.append(area)

                # Розвідники генерують нові маршрути
            for _ in range(self.num_scouts):
                new_areas.append(self.random_route())

                # Оновлення найкращого маршруту
            for route in new_areas:
                distance = self.calculate_route_distance(route)
                if distance < best_distance:
                    best_route = route
                    best_distance = distance

                    # Вибір кращих ділянок
            areas = sorted(new_areas, key=self.calculate_route_distance)[:self.num_areas]

        self.execution_time = time.time() - start_time
        return best_route, best_distance


def generate_distance_matrix(num_cities, min_distance=5, max_distance=150, seed=None):
    if seed is not None:
        np.random.seed(seed)
    matrix = np.random.randint(min_distance, max_distance, size=(num_cities, num_cities))
    np.fill_diagonal(matrix, 0)
    return (matrix + matrix.T) // 2  # Симетрична матриця


if __name__ == "__main__":
    num_cities = 300
    distance_matrix = generate_distance_matrix(num_cities, seed=42)

    # Налаштування параметрів алгоритму
    num_areas = 5
    num_foragers = 50
    num_scouts = 10
    max_iterations = 500

    # Ініціалізація та запуск алгоритму
    bee_algorithm = BeeAlgorithm(distance_matrix, num_areas, num_foragers, num_scouts, max_iterations)
    best_route, best_distance = bee_algorithm.run()

    # Виведення результатів
    print("Найкращий маршрут:")
    for i in range(0, len(best_route), 20):
        print(best_route[i:i + 20])
    print(f"Довжина найкращого маршруту: {best_distance}")