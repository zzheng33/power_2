#!/bin/bash

home_dir=$HOME
benchmark_dir="${home_dir}/benchmark/ECP/XSBench/cuda"


# "$benchmark_dir/XSBench" -m event -s large
for i in {1..5}; do
    "$benchmark_dir/XSBench" -m event -s large
done

