#!/bin/bash

set -e

mkdir -p build
g++ -O2 *.cpp -o build/main

./build/main "$@"