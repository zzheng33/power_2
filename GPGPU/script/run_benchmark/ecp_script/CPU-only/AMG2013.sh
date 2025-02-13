#!/bin/bash

home_dir=$HOME
benchmark_dir="/home/cc/benchmark/ECP/CPU-only/AMG2013/test"

mpirun -n 1 amg2013 -pooldist 0 -r 6 6 6