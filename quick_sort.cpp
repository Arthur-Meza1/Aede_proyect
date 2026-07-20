#include "quick_sort.h"
#include "contadores.h"

static int particion(std::vector<int>& arr, int bajo, int alto) {
    int pivote = arr[alto];
    int i = bajo - 1;

    for (int j = bajo; j < alto; ++j) {
        ++g_contadores.comparaciones;
        if (arr[j] < pivote) {
            ++i;
            ++g_contadores.intercambios;
            std::swap(arr[i], arr[j]);
        }
    }
    ++g_contadores.intercambios;
    std::swap(arr[i + 1], arr[alto]);
    return i + 1;
}

static void quickSortRec(std::vector<int>& arr, int bajo, int alto) {
    if (bajo < alto) {
        int indicePivote = particion(arr, bajo, alto);
        quickSortRec(arr, bajo, indicePivote - 1);
        quickSortRec(arr, indicePivote + 1, alto);
    }
}

void quickSort(std::vector<int>& arr) {
    if (arr.size() <= 1) return;
    quickSortRec(arr, 0, static_cast<int>(arr.size()) - 1);
}
