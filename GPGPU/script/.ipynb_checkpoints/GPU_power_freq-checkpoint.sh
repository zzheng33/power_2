#!/bin/bash

# List of GPU core frequencies (MHz)
FREQS=(225 250 275 300 325 350 375 400 425 450 475 500 525 550 575 600 625 650 675 700 725 750 775 800 825 850 875 900 925 950 975 1000 1025 1050 1075 1100 1125 1150 1175 1200 1225 1250 1275 1300 1325 1350 1375 1410)

# Output file
OUTPUT_FILE="gpu_power_freq_log.csv"
echo "Frequency (MHz),Max Power (W)" > $OUTPUT_FILE

# Initialize max power tracking
GLOBAL_MAX_POWER=0
BEST_FREQ=0

for FREQ in "${FREQS[@]}"; do
    echo "Setting GPU clock frequency to $FREQ MHz"
    sudo nvidia-smi -lgc $FREQ,$FREQ  # Lock GPU core clock

    # Allow time for frequency change
    sleep 2

    # Run the application
    # ./run_benchmark/altis_script/level2/raytracing.sh &

    # APP_PID=$!
    MAX_POWER=0

    # Monitor GPU power for 10 seconds
    for i in {1..5}; do
        POWER=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits | awk '{print $1}')
        UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | awk '{print $1}')
        
        if (( $(echo "$POWER > $MAX_POWER" | bc -l) )); then
            MAX_POWER=$POWER
        fi

        # echo "GPU Utilization: $UTIL% - Power: $POWER W"
        sleep 0.2
    done

    # # Kill the application
    # kill $APP_PID
    # wait $APP_PID 2>/dev/null

    echo "Frequency: $FREQ MHz - Max Power: $MAX_POWER W"
    echo "$FREQ,$MAX_POWER" >> $OUTPUT_FILE

    # Update max power record
    if (( $(echo "$MAX_POWER > $GLOBAL_MAX_POWER" | bc -l) )); then
        GLOBAL_MAX_POWER=$MAX_POWER
        BEST_FREQ=$FREQ
    fi
done

sudo nvidia-smi -rgc

# echo "Best Frequency: $BEST_FREQ MHz with Max Power: $GLOBAL_MAX_POWER W"
# echo "Best Frequency: $BEST_FREQ MHz, Max Power: $GLOBAL_MAX_POWER W" >> $OUTPUT_FILE
