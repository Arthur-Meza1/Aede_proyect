#include <benchmark/benchmark.h>
#include "bubble_sort.h"
#include "insertion_sort.h"
#include "merge_sort.h"
#include "quick_sort.h"
#include "heap_sort.h"
#include "contadores.h"

static void BM_BubbleSort(benchmark::State& state) {
    int n = state.range(0);
    Distribucion dist = static_cast<Distribucion>(state.range(1));

    for (auto _ : state) {
        state.PauseTiming();
        auto datos = generarDatos(n, dist);
        g_contadores = {0, 0};
        state.ResumeTiming();

        bubbleSort(datos);
        benchmark::DoNotOptimize(datos.data());
    }

    state.counters["Comparaciones"] = g_contadores.comparaciones;
    state.counters["Intercambios"]   = g_contadores.intercambios;
    state.counters["RAM_Auxiliar_KB"] = 0.0;
}

static void BM_InsertionSort(benchmark::State& state) {
    int n = state.range(0);
    Distribucion dist = static_cast<Distribucion>(state.range(1));

    for (auto _ : state) {
        state.PauseTiming();
        auto datos = generarDatos(n, dist);
        g_contadores = {0, 0};
        state.ResumeTiming();

        insertionSort(datos);
        benchmark::DoNotOptimize(datos.data());
    }

    state.counters["Comparaciones"] = g_contadores.comparaciones;
    state.counters["Intercambios"]   = g_contadores.intercambios;
    state.counters["RAM_Auxiliar_KB"] = 0.0;
}

static void BM_MergeSort(benchmark::State& state) {
    int n = state.range(0);
    Distribucion dist = static_cast<Distribucion>(state.range(1));
    double ramAux = (n * static_cast<double>(sizeof(int))) / 1024.0;

    for (auto _ : state) {
        state.PauseTiming();
        auto datos = generarDatos(n, dist);
        g_contadores = {0, 0};
        state.ResumeTiming();

        mergeSort(datos);
        benchmark::DoNotOptimize(datos.data());
    }

    state.counters["Comparaciones"]  = g_contadores.comparaciones;
    state.counters["Intercambios"]    = g_contadores.intercambios;
    state.counters["RAM_Auxiliar_KB"] = ramAux;
}

static void BM_QuickSort(benchmark::State& state) {
    int n = state.range(0);
    Distribucion dist = static_cast<Distribucion>(state.range(1));

    for (auto _ : state) {
        state.PauseTiming();
        auto datos = generarDatos(n, dist);
        g_contadores = {0, 0};
        state.ResumeTiming();

        quickSort(datos);
        benchmark::DoNotOptimize(datos.data());
    }

    state.counters["Comparaciones"] = g_contadores.comparaciones;
    state.counters["Intercambios"]   = g_contadores.intercambios;
    state.counters["RAM_Auxiliar_KB"] = 0.0;
}

static void BM_HeapSort(benchmark::State& state) {
    int n = state.range(0);
    Distribucion dist = static_cast<Distribucion>(state.range(1));

    for (auto _ : state) {
        state.PauseTiming();
        auto datos = generarDatos(n, dist);
        g_contadores = {0, 0};
        state.ResumeTiming();

        heapSort(datos);
        benchmark::DoNotOptimize(datos.data());
    }

    state.counters["Comparaciones"] = g_contadores.comparaciones;
    state.counters["Intercambios"]   = g_contadores.intercambios;
    state.counters["RAM_Auxiliar_KB"] = 0.0;
}

static void SlowSortArgs(benchmark::internal::Benchmark* b) {
    for (int n : {1000, 5000, 10000})
        for (int d = 0; d < 4; ++d)
            b->Args({n, d});
}

static void FastSortArgs(benchmark::internal::Benchmark* b) {
    for (int n : {1000, 10000, 100000, 1000000})
        for (int d = 0; d < 4; ++d)
            b->Args({n, d});
}

BENCHMARK(BM_BubbleSort)  ->Apply(SlowSortArgs)->Repetitions(30)->DisplayAggregatesOnly(false);
BENCHMARK(BM_InsertionSort)->Apply(SlowSortArgs)->Repetitions(30)->DisplayAggregatesOnly(false);
BENCHMARK(BM_MergeSort)   ->Apply(FastSortArgs)->Repetitions(30)->DisplayAggregatesOnly(false);
BENCHMARK(BM_QuickSort)   ->Apply(FastSortArgs)->Repetitions(30)->DisplayAggregatesOnly(false);
BENCHMARK(BM_HeapSort)    ->Apply(FastSortArgs)->Repetitions(30)->DisplayAggregatesOnly(false);

BENCHMARK_MAIN();
