cmake_minimum_required(VERSION 3.14)
project(experimentos_sorting LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
    googlebenchmark
    GIT_REPOSITORY https://github.com/google/benchmark.git
    GIT_TAG v1.8.3
)

set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "")

FetchContent_MakeAvailable(googlebenchmark)

add_executable(ejecutable_experimentos
    contadores.cpp
    bubble_sort.cpp
    insertion_sort.cpp
    quick_sort.cpp
    merge_sort.cpp
    heap_sort.cpp
    main.cpp
)

target_link_libraries(ejecutable_experimentos PRIVATE benchmark::benchmark)
