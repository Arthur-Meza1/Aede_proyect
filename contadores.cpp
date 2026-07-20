#include "contadores.h"
#include <random>
#include <algorithm>
#include <numeric>

thread_local Contadores g_contadores{0, 0};

std::vector<int> generarDatos(int n, Distribucion dist) {
    std::vector<int> datos(n);
    std::mt19937 rng(std::random_device{}());

    std::iota(datos.begin(), datos.end(), 0);

    switch (dist) {
        case Distribucion::ALEATORIO:
            std::shuffle(datos.begin(), datos.end(), rng);
            break;
        case Distribucion::ORDENADO:
            break;
        case Distribucion::INVERSO:
            std::reverse(datos.begin(), datos.end());
            break;
        case Distribucion::PARCIALMENTE_ORDENADO: {
            int numPares = std::max(1, n / 10);
            std::vector<int> indices(n);
            std::iota(indices.begin(), indices.end(), 0);
            std::shuffle(indices.begin(), indices.end(), rng);
            indices.resize(std::min(2 * numPares, n));
            for (size_t i = 0; i + 1 < indices.size(); i += 2) {
                std::swap(datos[indices[i]], datos[indices[i + 1]]);
            }
            break;
        }
    }

    return datos;
}
