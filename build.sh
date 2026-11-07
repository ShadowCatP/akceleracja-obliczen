#!/bin/bash

set -e

mkdir -p build
g++ -O2 -mavx512f *.cpp -o build/main

./build/main "$@"