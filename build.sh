#!/bin/bash

set -e

mkdir -p build
g++ main.cpp -o build/main

./build/main