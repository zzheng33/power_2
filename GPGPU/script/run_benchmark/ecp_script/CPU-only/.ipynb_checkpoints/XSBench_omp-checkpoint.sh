#!/bin/bash

home_dir=$HOME
benchmark_dir="${home_dir}/benchmark/ECP/XSBench/openmp-threading"
benchmark_dir="/home/cc/benchmark/ECP/XSBench/openmp-threading"
"$benchmark_dir/XSBench"  -s large
