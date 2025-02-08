#!/bin/bash

# suite 0: ECP 
# suite 1: ALTIS
# suite 2: npb

python3 exp_power_motif.py --suite 1 

sleep 5


./power_util/set_uncore_freq.sh 2.2 2.2

TARGET_DIR="../data/"

# Find all .csv files under the target directory and make them writable
sudo find "$TARGET_DIR" -type f -name "*.csv" -exec chown $(whoami):$(whoami) {} \;