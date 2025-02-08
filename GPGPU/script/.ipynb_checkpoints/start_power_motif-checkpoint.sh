#!/bin/bash

# suite 0: ECP 
# suite 1: ALTIS
# suite 2: npb

python3 exp_power_motif.py --suite 2 --test 0  --dynamic_ufs_gpuP 0 --dynamic_ufs_mem 0 --uncore_0 2.2 --uncore_1 2.2 --pcm 1 --inc_ts 200 --dec_ts 500 --history 5 --dual_cap 0 --burst_up 0.4 --burst_low 0.2 --ups 0 

sleep 3


sudo mv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/*.csv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/max_uncore 
sudo mv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/mem_throughput/*.csv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/mem_throughput/max_uncore






./power_util/set_uncore_freq.sh 2.2 2.2

TARGET_DIR="../data/"

# Find all .csv files under the target directory and make them writable
sudo find "$TARGET_DIR" -type f -name "*.csv" -exec chown $(whoami):$(whoami) {} \;