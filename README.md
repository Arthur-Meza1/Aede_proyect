# Proyecto de Benchmarking de Algoritmos de Ordenamiento

Evaluacion estadistica del rendimiento de 5 algoritmos de ordenamiento clasicos
usando el framework Google Benchmark. Disenado para generar datos exportables
para Analisis Exploratorio de Datos (EDA) con Python (Pandas/Seaborn).

## Algoritmos Evaluados

| Algoritmo      | Complejidad    | Clasificacion     |
|----------------|----------------|-------------------|
| Bubble Sort    | O(n^2)         | Por intercambio   |
| Insertion Sort | O(n^2)         | Por insercion     |
| Merge Sort     | O(n log n)     | Divide y venceras |
| Quick Sort     | O(n log n)     | Divide y venceras |
| Heap Sort      | O(n log n)     | Por seleccion     |

## Variables Independientes

- **Tamano de entrada (n):**
  - Algoritmos O(n^2): 1.000, 5.000, 10.000 elementos
  - Algoritmos O(n log n): 1.000, 10.000, 100.000, 1.000.000 elementos

- **Distribucion inicial de datos:**
  - `ALEATORIO` — permutacion uniforme aleatoria
  - `ORDENADO` — datos ya ordenados ascendentemente
  - `INVERSO` — datos ordenados descendentemente
  - `PARCIALMENTE_ORDENADO` — ~90% de elementos en su posicion correcta

## Variables Dependientes (Metricas)

Por cada ejecucion se registran:

| Metrica          | Unidad    | Descripcion                              |
|------------------|-----------|------------------------------------------|
| Tiempo real      | ns        | Tiempo de pared (wall clock)             |
| Tiempo CPU       | ns        | Tiempo de CPU                            |
| Comparaciones    | enteros   | Conteo exacto de comparaciones entre elementos |
| Intercambios     | enteros   | Conteo exacto de swaps / movimientos     |
| RAM Auxiliar     | KB        | Memoria extra teorica usada por el algoritmo |

### RAM Auxiliar por Algoritmo

| Algoritmo      | RAM Auxiliar       |
|----------------|--------------------|
| Bubble Sort    | 0 KB (in-situ)     |
| Insertion Sort | 0 KB (in-situ)     |
| Quick Sort     | 0 KB (in-situ)*    |
| Heap Sort      | 0 KB (in-situ)     |
| Merge Sort     | `(n * sizeof(int)) / 1024.0` KB |

*Quick Sort usa espacio en la pila de recursion (O(log n)), no medido aqui.

## Requisitos

- CMake >= 3.14
- Compilador C++17 (GCC >= 7, Clang >= 5, o MSVC >= 2017)
- Git (para que FetchContent descargue Google Benchmark)

## Compilacion

```bash
# Configurar el proyecto (descarga e incluye Google Benchmark v1.8.3 via FetchContent)
cmake -B build -S .

# Compilar
cmake --build build

# El binario se genera en:
#   build/ejecutable_experimentos
```

## Ejecucion

```bash
# Ejecutar todos los benchmarks
./build/ejecutable_experimentos

# Ejecutar solo un algoritmo especifico
./build/ejecutable_experimentos --benchmark_filter="BM_QuickSort"

# Ejecutar solo con un tamano especifico
./build/ejecutable_experimentos --benchmark_filter="BM_MergeSort/100000"

# Limitar el tiempo por benchmark (util para ejecuciones largas)
./build/ejecutable_experimentos --benchmark_min_time=1s
```

### Exportacion de Datos para EDA en Python

Google Benchmark permite exportar los resultados en JSON o CSV para su
procesamiento externo:

```bash
# Exportar a JSON
./build/ejecutable_experimentos --benchmark_out=resultados.json --benchmark_out_format=json

# Exportar a CSV
./build/ejecutable_experimentos --benchmark_out=resultados.csv --benchmark_out_format=csv
```

### Ejemplo de Carga en Python (Pandas)

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Cargar datos desde CSV
df = pd.read_csv("resultados.csv")

# Diagrama de caja: tiempo por algoritmo y distribucion
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x="algorithm", y="real_time", hue="distribution")
plt.yscale("log")
plt.show()

# Disparo: comparaciones vs n por algoritmo
plt.figure(figsize=(10, 5))
sns.scatterplot(data=df, x="n", y="comparaciones", hue="algorithm", style="distribution")
plt.xscale("log")
plt.yscale("log")
plt.show()
```

## Estructura del Proyecto

```
proyecto_sorting/
├── CMakeLists.txt          # Build system (C++17, FetchContent)
├── contadores.h            # Estructura Contadores, enum Distribucion
├── contadores.cpp          # Generacion de datos, variable thread_local
├── bubble_sort.h/.cpp      # Bubble Sort instrumentado
├── insertion_sort.h/.cpp   # Insertion Sort instrumentado
├── quick_sort.h/.cpp       # Quick Sort instrumentado
├── merge_sort.h/.cpp       # Merge Sort instrumentado
├── heap_sort.h/.cpp        # Heap Sort instrumentado
├── main.cpp                # Benchmarks con Google Benchmark
└── README.md               # Este archivo
```

## Instrumentacion

Cada algoritmo incrementa contadores globales thread-local (`g_contadores`)
durante su ejecucion:

- `g_contadores.comparaciones` — cada vez que se comparan dos elementos
- `g_contadores.intercambios` — cada swap, asignacion o movimiento de elemento

Los contadores se reinician a `{0, 0}` antes de cada llamada al algoritmo
dentro del bucle de benchmark para evitar contaminacion entre iteraciones.

## Repeticiones Estadisticas

Cada configuracion (algoritmo x tamano x distribucion) se ejecuta
**30 repeticiones**. Google Benchmark reporta automaticamente la media,
mediana, desviacion estandar y coeficiente de variacion para todas las
metricas registradas, permitiendo analisis de varianza y deteccion de
outliers.

## Notas

- La generacion de datos se realiza con `state.PauseTiming()` para que el
  tiempo de generacion no contamine la medicion del algoritmo.
- Se usa `benchmark::DoNotOptimize()` para evitar que el compilador elimine
  codigo "muerto" en los benchmarks.
- Los contadores son `thread_local` para permitir ejecucion paralela segura
  si Google Benchmark decidiera lanzar varios hilos.
