using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace ModCode
{
    class MultiPhaseSort
    {
        // Параметри файлу
        private const int FileSizeMB = 2048;  // Розмір файлу у 2 ГБ
        private const int NumbersPerMB = 250000;  // Кількість цілих чисел у 1 MB
        private const int TotalNumbers = FileSizeMB * NumbersPerMB;  // Загальна кількість чисел у файлі

        // Обмежуємо розмір доступної ОП для сортування
        private const int AvailableMemoryMB = 512;  // Штучно обмежуємо доступну ОП до 512MB
        private const int ChunkSize = AvailableMemoryMB * NumbersPerMB;  // Розмір чанка (512MB)

        static void Main()
        {
            string filePath = "random_numbers.txt";

            // 1. Генерація файлу з випадковими числами
            GenerateRandomNumbersFile(filePath, TotalNumbers);

            // 2. Багатофазне сортування файлу з використанням m допоміжних файлів
            int m = 4; // кількість файлів
            MultiPhaseSortFile(filePath, m);
        }

        // Генерація випадкових чисел
        private static void GenerateRandomNumbersFile(string filePath, int count)
        {
            Random rand = new Random();
            using (StreamWriter writer = new StreamWriter(filePath))
            {
                for (int i = 0; i < count; i++)
                {
                    writer.WriteLine(rand.Next(int.MinValue, int.MaxValue));
                }
            }
            Console.WriteLine("Файл з випадковими числами згенеровано.");
        }

        // Багатофазне сортування файлу
        private static void MultiPhaseSortFile(string filePath, int m)
        {
            // Створюємо масив допоміжних файлів
            string[] tempFiles = new string[m];
            for (int i = 0; i < m; i++)
            {
                tempFiles[i] = $"temp_chunk_{i}.txt";
            }

            // 1. Розбиваємо файл на серії і сортуємо їх
            List<string> chunkFiles = SplitAndSortChunks(filePath, tempFiles, ChunkSize, m);

            // 2. Зливаємо відсортовані частини у результуючий файл
            string sortedFilePath = "sorted_numbers.txt";
            MergeSortedChunks(chunkFiles, sortedFilePath);

            Console.WriteLine("Файл відсортовано та збережено у 'sorted_numbers.txt'.");
        }

        // Генерація чисел Фібоначчі порядку p
        private static List<int> GenerateFibonacciSequence(int p, int count)
        {
            List<int> fibonacci = Enumerable.Repeat(0, p).ToList(); // Початкові p нулів
            fibonacci.Add(1); // Додаємо 1 як (p+1)-й елемент

            // Генеруємо решту послідовності
            for (int i = p + 1; i < count; i++)
            {
                int sum = 0;
                for (int j = i - (p + 1); j < i; j++)
                {
                    sum += fibonacci[j];
                }
                fibonacci.Add(sum);
            }

            return fibonacci;
        }

        // Розбиваємо великий файл на відсортовані частини на основі Фібоначчі
        private static List<string> SplitAndSortChunks(string filePath, string[] tempFiles, int chunkSize, int m)
        {
            int p = m - 2; // Порядок Фібоначчі
            List<int> fibonacciSeries = GenerateFibonacciSequence(p, m - 1);  // Генеруємо послідовність

            List<string> chunkFiles = new List<string>(tempFiles);
            using (StreamReader reader = new StreamReader(filePath))
            {
                int chunkIndex = 0;
                int fileIndex = 0;  // Індекс файлу для запису
                int remainingSeries = fibonacciSeries[fileIndex];  // Лічильник серій для поточного файлу

                while (!reader.EndOfStream)
                {
                    List<int> numbers = new List<int>();
                    for (int i = 0; i < chunkSize && !reader.EndOfStream; i++)
                    {
                        numbers.Add(int.Parse(reader.ReadLine()));
                    }

                    // Сортуємо числа
                    numbers.Sort();
                    using (StreamWriter writer = new StreamWriter(tempFiles[fileIndex], append: true))
                    {
                        foreach (var number in numbers)
                        {
                            writer.WriteLine(number);
                        }
                    }

                    chunkIndex++;
                    remainingSeries--;

                    // Перехід до наступного файлу
                    if (remainingSeries == 0 && fileIndex < m - 2)
                    {
                        fileIndex++;
                        remainingSeries = fibonacciSeries[fileIndex];
                    }
                }
            }

            return chunkFiles;
        }

        // Функція для злиття відсортованих частин
        private static void MergeSortedChunks(List<string> chunkFiles, string outputFilePath)
        {
            var readers = chunkFiles.Select(file => new StreamReader(file)).ToList();
            using (StreamWriter writer = new StreamWriter(outputFilePath))
            {
                var heap = new SortedDictionary<int, Queue<int>>();

                for (int i = 0; i < readers.Count; i++)
                {
                    if (!readers[i].EndOfStream)
                    {
                        int number = int.Parse(readers[i].ReadLine());
                        if (!heap.ContainsKey(number))
                        {
                            heap[number] = new Queue<int>();
                        }
                        heap[number].Enqueue(i);
                    }
                }

                while (heap.Count > 0)
                {
                    var minEntry = heap.First();
                    int minValue = minEntry.Key;
                    int fileIndex = minEntry.Value.Dequeue();
                    if (minEntry.Value.Count == 0)
                    {
                        heap.Remove(minValue);
                    }

                    writer.WriteLine(minValue);

                    if (!readers[fileIndex].EndOfStream)
                    {
                        int nextValue = int.Parse(readers[fileIndex].ReadLine());
                        if (!heap.ContainsKey(nextValue))
                        {
                            heap[nextValue] = new Queue<int>();
                        }
                        heap[nextValue].Enqueue(fileIndex);
                    }
                }
            }

            foreach (var reader in readers)
            {
                reader.Close();
            }
        }
    }
}
