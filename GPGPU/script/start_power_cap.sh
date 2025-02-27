#!/bin/bash

# List of benchmark names
ecp_benchmarks=("XSBench" "miniGAN" "CRADL" "sw4lite" "Laghos" "bert_large" "UNet" "Resnet50" "lammps" "gromacs")

# Run exp_power_cap.py 5 times
for i in {1..5}; do
    echo "Running experiment $i..."
    python3 exp_power_cap.py --suite 0

    sleep 5  # Wait before processing

    # Create run directory
    run_dir="run${i}"
    mkdir -p "$run_dir"

    # Move benchmark folders to run directory
    for benchmark in "${ecp_benchmarks[@]}"; do
        if [ -d "$benchmark" ]; then
            mv "$benchmark" "$run_dir/"
        fi
    done
done

# Change ownership of data directory
sudo chown -R cc:cc ../data/

# echo "All experiments completed and files organized."


# #!/bin/bash

# # suite 0: ECP 
# # suite 1: ALTIS
# # suite 2: npb

# python3 exp_power_cap.py --suite 0 

# sleep 5


# # ./power_util/set_uncore_freq.sh 2.2 2.2