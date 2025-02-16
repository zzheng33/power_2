#!/bin/bash

# suite 0: ECP 
# suite 1: ALTIS
# suite 2: npb

python3 exp_power_cap.py --suite 1 
sleep 3
# ./power_util/set_uncore_freq.sh 2.2 2.2

TARGET_DIR="/home/cc/power/GPGPU/data/altis_power_cap_res/"

# Change ownership of all CSV files to the current user
sudo find "$TARGET_DIR" -type f -name "*.csv" -exec chown $(whoami):$(whoami) {} \;

# Make all CSV files writable by the owner
sudo find "$TARGET_DIR" -type f -name "*.csv" -exec chmod u+w {} \;

# Make all files and directories writable for the owner
sudo find "$TARGET_DIR" -type f -exec chmod u+w {} \;
sudo find "$TARGET_DIR" -type d -exec chmod u+w {} \