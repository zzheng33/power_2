#!/bin/bash

home_dir=$HOME
benchmark_dir="${home_dir}/benchmark/ECP/RSBench/openmp-threading"
benchmark_dir="/home/cc/benchmark/ECP/RSBench/openmp-threading"
"$benchmark_dir/rsbench" -s large
