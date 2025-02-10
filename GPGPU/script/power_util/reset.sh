#!/bin/bash


sudo nvidia-smi -lgc 0,1410
sudo nvidia-smi -pl 250


cap_uw=$((540 * 500000))  # Convert W to uW
#Apply the cap to both sockets
echo $cap_uw | sudo tee /sys/class/powercap/intel-rapl:0/constraint_0_power_limit_uw
echo $cap_uw | sudo tee /sys/class/powercap/intel-rapl:1/constraint_0_power_limit_uw
echo $cap_uw | sudo tee /sys/class/powercap/intel-rapl:0/constraint_1_power_limit_uw
echo $cap_uw | sudo tee /sys/class/powercap/intel-rapl:1/constraint_1_power_limit_uw

