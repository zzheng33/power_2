#!/bin/bash

home_dir=$HOME
benchmark_dir="${home_dir}/benchmark/ECP/NAMD/"

cd ${benchmark_dir}

./namd3 +p8 +devices 0 ./stmv/stmv_nve_cuda.namd
