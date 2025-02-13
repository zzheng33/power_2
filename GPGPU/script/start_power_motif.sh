#!/bin/bash

# suite 0: ECP 
# suite 1: ALTIS
# suite 2: npb

python3 exp_power_motif.py --suite 0

# sleep 3

# sudo mv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/*.csv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/max_uncore 
# sudo mv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/mem_throughput/*.csv /home/cc/power/GPGPU/data/npb_power_res/no_power_shift/mem_throughput/max_uncore






./power_util/set_uncore_freq.sh 2.2 2.2

TARGET_DIR="../data/"

# Find all .csv files under the target directory and make them writable
sudo find "$TARGET_DIR" -type f -name "*.csv" -exec chown $(whoami):$(whoami) {} \;