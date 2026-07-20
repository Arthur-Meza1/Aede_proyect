#ifndef CONTADORES_H
#define CONTADORES_H

#include <vector>

struct Contadores {
    long long comparaciones = 0;
    long long intercambios = 0;
};

extern thread_local Contadores g_contadores;

enum class Distribucion { ALEATORIO, ORDENADO, INVERSO, PARCIALMENTE_ORDENADO };

std::vector<int> generarDatos(int n, Distribucion dist);

#endif
