#!/bin/bash

## 1410

freq_max_limit=$1
sudo nvidia-smi -lgc 0,$freq_max_limit


