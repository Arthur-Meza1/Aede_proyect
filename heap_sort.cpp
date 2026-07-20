#include "heap_sort.h"
#include "contadores.h"

static void heapify(std::vector<int>& arr, int n, int i) {
    int largest = i;
    int izquierda = 2 * i + 1;
    int derecha = 2 * i + 2;

    if (izquierda < n) {
        ++g_contadores.comparaciones;
        if (arr[izquierda] > arr[largest]) {
            largest = izquierda;
        }
    }

    if (derecha < n) {
        ++g_contadores.comparaciones;
        if (arr[derecha] > arr[largest]) {
            largest = derecha;
        }
    }

    if (largest != i) {
        ++g_contadores.intercambios;
        std::swap(arr[i], arr[largest]);
        heapify(arr, n, largest);
    }
}

void heapSort(std::vector<int>& arr) {
    int n = static_cast<int>(arr.size());

    for (int i = n / 2 - 1; i >= 0; --i) {
        heapify(arr, n, i);
    }

    for (int i = n - 1; i > 0; --i) {
        ++g_contadores.intercambios;
        std::swap(arr[0], arr[i]);
        heapify(arr, i, 0);
    }
}
