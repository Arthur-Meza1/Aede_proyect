#include "bubble_sort.h"
#include "contadores.h"

void bubbleSort(std::vector<int>& arr) {
    int n = static_cast<int>(arr.size());
    for (int i = 0; i < n - 1; ++i) {
        for (int j = 0; j < n - i - 1; ++j) {
            ++g_contadores.comparaciones;
            if (arr[j] > arr[j + 1]) {
                ++g_contadores.intercambios;
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }
}
