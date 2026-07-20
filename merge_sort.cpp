#include "merge_sort.h"
#include "contadores.h"
#include <vector>

static void merge(std::vector<int>& arr, int izquierda, int medio, int derecha) {
    int n1 = medio - izquierda + 1;
    int n2 = derecha - medio;

    std::vector<int> L(n1);
    std::vector<int> R(n2);

    for (int i = 0; i < n1; ++i) {
        L[i] = arr[izquierda + i];
        ++g_contadores.intercambios;
    }
    for (int j = 0; j < n2; ++j) {
        R[j] = arr[medio + 1 + j];
        ++g_contadores.intercambios;
    }

    int i = 0, j = 0, k = izquierda;

    while (i < n1 && j < n2) {
        ++g_contadores.comparaciones;
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            ++i;
        } else {
            arr[k] = R[j];
            ++j;
        }
        ++g_contadores.intercambios;
        ++k;
    }

    while (i < n1) {
        arr[k] = L[i];
        ++i;
        ++k;
        ++g_contadores.intercambios;
    }

    while (j < n2) {
        arr[k] = R[j];
        ++j;
        ++k;
        ++g_contadores.intercambios;
    }
}

static void mergeSortRec(std::vector<int>& arr, int izquierda, int derecha) {
    if (izquierda < derecha) {
        int medio = izquierda + (derecha - izquierda) / 2;
        mergeSortRec(arr, izquierda, medio);
        mergeSortRec(arr, medio + 1, derecha);
        merge(arr, izquierda, medio, derecha);
    }
}

void mergeSort(std::vector<int>& arr) {
    if (arr.size() <= 1) return;
    mergeSortRec(arr, 0, static_cast<int>(arr.size()) - 1);
}
