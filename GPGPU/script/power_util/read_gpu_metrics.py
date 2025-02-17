import time
import os
import csv
import argparse
import psutil
import subprocess  

# GPU Details for A100-40GB
NUM_SMS = 108           # Number of Streaming Multiprocessors (SMs)
CUDA_CORES_PER_SM = 64  # CUDA Cores per SM
FP32_INSTRUCTIONS_PER_CYCLE = 2  # Ampere: 2 FP32 instructions per cycle
FP16_INSTRUCTIONS_PER_CYCLE = 4  # Ampere: FP16 can execute 4 operations per cycle

# Function to run shell commands and return output
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


# # Function to get real-time SM clock speed (MHz)
# def get_sm_clock():
#     output = run_command("nvidia-smi --query-gpu=clocks.sm --format=csv,noheader,nounits")
#     return float(output) * 1e6  # Convert MHz to Hz


# Function to get DCGM metrics: fp32_active, fp64_active, fp16_active, sm_active
def get_dcgm_metrics():
    output = run_command("dcgmi dmon -e 1008,1007,1006,1002,100,155,1005 -d 300 -c 3")
    # print(output)
    lines = output.split("\n")
    fp16_active, fp32_active, fp64_active, sm_active, sm_clock, power, dram_active = 0,0,0,0,0,0,0
    for i in range(2, len(lines)):
        values = lines[i].split()
        
        fp16_active = float(values[2])
        fp32_active = float(values[3])
        fp64_active = float(values[4])
        sm_active = float(values[5])
        sm_clock = float(values[6])
        power = float(values[7])
        dram_active = float(values[8])
        
        if (fp32_active > 0 or fp64_active > 0 or fp16_active > 0) and sm_active > 0:
            return fp16_active, fp32_active, fp64_active, sm_active, sm_clock, power, dram_active
    
    return fp16_active, fp32_active, fp64_active, sm_active, sm_clock, power, dram_active

# Function to calculate real-time FLOPS
def calculate_flops(sm_clock_hz, fp_active, sm_active, precision="FP32"):
    if sm_clock_hz is None or fp_active is None or sm_active is None:
        return None

    if precision == "FP32":
        factor = FP32_INSTRUCTIONS_PER_CYCLE
    elif precision == "FP64":
        factor = 1  # FP64 has lower throughput
    elif precision == "FP16":
        factor = FP16_INSTRUCTIONS_PER_CYCLE
    else:
        return None

    flops = sm_clock_hz * fp_active * sm_active * NUM_SMS * CUDA_CORES_PER_SM * factor
    return flops / 1e12  # Convert to TFLOPS

# Function to monitor GPU performance
def monitor_gpu_performance(benchmark_pid, output_csv, interval=0.1):
    start_time = time.time()
    performance_data = []
    
    while psutil.pid_exists(benchmark_pid):
        time.sleep(interval)
        elapsed_time = time.time() - start_time
        # sm_clock_hz = get_sm_clock()
        fp16_active, fp32_active, fp64_active, sm_active, sm_clock_hz, power, dram_active = get_dcgm_metrics()

        # fp32_flops = calculate_flops(sm_clock_hz, fp32_active, sm_active, precision="FP32")
        # fp64_flops = calculate_flops(sm_clock_hz, fp64_active, sm_active, precision="FP64")
        # fp16_flops = calculate_flops(sm_clock_hz, fp16_active, sm_active, precision="FP16")
        
        row = [elapsed_time, sm_clock_hz, dram_active, fp16_active, fp32_active, fp64_active, int(power)]
        performance_data.append(row)
    
    with open(output_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        headers = ['Time (s)', 'SM Clock (MHz)', 'DRAM Active', 'FP16 Active', 'FP32 Active', 'FP64 Active', 'Power (W)']
        writer.writerow(headers)
        writer.writerows(performance_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor GPU performance.')
    parser.add_argument('--pid', type=int, help='PID of the benchmark process', required=True)
    parser.add_argument('--output_csv', type=str, help='Output CSV file path', required=True)
    args = parser.parse_args()
    
    monitor_gpu_performance(args.pid, args.output_csv)
