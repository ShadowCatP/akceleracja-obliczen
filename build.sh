#!/bin/bash

set -e

mkdir -p build
g++ -O2 main.cpp naive.cpp -o build/main

./build/main "$@"