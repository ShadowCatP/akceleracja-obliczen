#!/bin/bash

set -e

mkdir -p build
rm -f build/*.o
g++ -O2 -c main.cpp -o build/main.o
g++ -O2 -c naive.cpp -o build/naive.o
g++ -O2 -c utils.cpp -o build/utils.o
g++ -O2 -mavx2 -c avx2.cpp -o build/avx2.o
g++ -O2 -mavx512f -c avx512.cpp -o build/avx512.o
g++ build/*.o -o build/main

./build/main "$@"