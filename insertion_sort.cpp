#include "insertion_sort.h"
#include "contadores.h"

void insertionSort(std::vector<int>& arr) {
    int n = static_cast<int>(arr.size());
    for (int i = 1; i < n; ++i) {
        int key = arr[i];
        int j = i - 1;

        ++g_contadores.comparaciones;
        while (j >= 0 && arr[j] > key) {
            ++g_contadores.comparaciones;
            arr[j + 1] = arr[j];
            ++g_contadores.intercambios;
            --j;
        }
        arr[j + 1] = key;
        ++g_contadores.intercambios;
    }
}
