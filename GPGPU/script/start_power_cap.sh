#!/bin/bash

# suite 0: ECP 
# suite 1: ALTIS
# suite 2: npb

python3 exp_power_cap.py --suite 0 --benchmark gromacs

sleep 3

# ./power_util/set_uncore_freq.sh 2.2 2.2




sudo chown -R cc:cc ../data/

