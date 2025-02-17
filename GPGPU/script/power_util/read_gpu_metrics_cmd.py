import subprocess
import time
import csv

# GPU Details for A100-40GB
NUM_SMS = 108           # Number of Streaming Multiprocessors (SMs)
CUDA_CORES_PER_SM = 64  # CUDA Cores per SM
FP32_INSTRUCTIONS_PER_CYCLE = 2  # Ampere: 2 FP32 instructions per cycle
FP16_INSTRUCTIONS_PER_CYCLE = 4  # Ampere: FP16 can execute 4 operations per cycle

# Log file setup
csv_filename = "gpu_performance_log.csv"

# Function to run shell commands and return output
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running command: {command}\n{e}")
        return None

# Function to get real-time SM clock speed (MHz)
def get_sm_clock():
    output = run_command("nvidia-smi --query-gpu=clocks.sm --format=csv,noheader,nounits")
    try:
        return float(output) * 1e6  # Convert MHz to Hz
    except ValueError:
        return None

# Function to get DCGM metrics: fp32_active, fp64_active, fp16_active, sm_active
def get_dcgm_metrics():
    output = run_command("dcgmi dmon -e 1008,1007,1006,1002,100,155 -d 300 -c 3")
    # print(output)
    lines = output.split("\n")
    fp16_active, fp32_active, fp64_active, sm_active, sm_clock, power = 0,0,0,0,0,0
    for i in range(2, len(lines)):
        values = lines[i].split()
        
        fp16_active = float(values[2])
        fp32_active = float(values[3])
        fp64_active = float(values[4])
        sm_active = float(values[5])
        sm_clock = float(values[6])
        power = float(values[7])
        
        if (fp32_active > 0 or fp64_active > 0 or fp16_active > 0) and sm_active > 0:
            return fp32_active, fp64_active, fp16_active, sm_active
    
    return fp32_active, fp64_active, fp16_active, sm_active

# Function to calculate real-time FLOPS
def calculate_flops(sm_clock_hz, fp_active, sm_active, precision="FP32"):
    if sm_clock_hz is None or fp_active is None or sm_active is None:
        return None

    if precision == "FP32":
        factor = FP32_INSTRUCTIONS_PER_CYCLE
    elif precision == "FP64":
        factor = 1  # FP64 has lower throughput
    elif precision == "FP16":
        factor = FP16_INSTRUCTIONS_PER_CYCLE  # FP16 executes 4 instructions per cycle
    else:
        return None

    flops = sm_clock_hz * fp_active * sm_active * NUM_SMS * CUDA_CORES_PER_SM * factor
    return flops / 1e12  # Convert to TFLOPS

# Start monitoring
# print("Monitoring GPU Performance (Press Ctrl+C to stop)...")

# Write CSV header
with open(csv_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "SM Clock (MHz)", "FP32 Active", "FP64 Active", "FP16 Active", "SM Active", "FP32 FLOPS (TFLOPS)", "FP64 FLOPS (TFLOPS)", "FP16 FLOPS (TFLOPS)"])

try:
    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Get metrics
        sm_clock_hz = get_sm_clock()
        fp32_active, fp64_active, fp16_active, sm_active = get_dcgm_metrics()

        # Compute FLOPS
        fp32_flops = calculate_flops(sm_clock_hz, fp32_active, sm_active, precision="FP32")
        fp64_flops = calculate_flops(sm_clock_hz, fp64_active, sm_active, precision="FP64")
        fp16_flops = calculate_flops(sm_clock_hz, fp16_active, sm_active, precision="FP16")

        # Print output
        print(f"[{timestamp}] SM Clock: {sm_clock_hz / 1e6 if sm_clock_hz else 'N/A'} MHz | FP32: {fp32_flops:.2f} TFLOPS | FP64: {fp64_flops:.2f} TFLOPS | FP16: {fp16_flops:.2f} TFLOPS")

        # Save to CSV
        with open(csv_filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, sm_clock_hz / 1e6 if sm_clock_hz else "N/A", fp32_active, fp64_active, fp16_active, sm_active, fp32_flops, fp64_flops, fp16_flops])

        time.sleep(0.1)  # Update every 0.5 seconds

except KeyboardInterrupt:
    print("\nMonitoring stopped. Data saved to", csv_filename)
