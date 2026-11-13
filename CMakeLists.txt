cmake_minimum_required(VERSION 3.15)
project(HeatSimulation LANGUAGES CXX CUDA)

if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
    set(CMAKE_CUDA_ARCHITECTURES 75)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SOURCES
    main.cpp
    naive.cpp
    utils.cpp
    avx2.cpp
    avx512.cpp
    cuda.cu
)

add_executable(main ${SOURCES})

if(NOT MSVC)
    set_source_files_properties(avx2.cpp PROPERTIES COMPILE_FLAGS "-mavx2")
    set_source_files_properties(avx512.cpp PROPERTIES COMPILE_FLAGS "-mavx512f")
endif()