import subprocess
import time
import csv

# GPU Details for A100-40GB
NUM_SMS = 108           # Number of Streaming Multiprocessors (SMs)
CUDA_CORES_PER_SM = 64  # CUDA Cores per SM
FP32_INSTRUCTIONS_PER_CYCLE = 2  # Ampere: 2 FP32 instructions per cycle

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

# Function to get DCGM metrics: fp32_active, fp64_active, sm_active
def get_dcgm_metrics():
    output = run_command("dcgmi dmon -e 1007,1006,1002 -d 20 -c 5")
    lines = output.split("\n")
    if len(lines) < 2:
        return None, None, None
    
    try:
        values = lines[6].split()
        fp32_active = float(values[2])  # FP32 utilization
        fp64_active = float(values[3])  # FP64 utilization
        sm_active = float(values[4])    # SM utilization
        return fp32_active, fp64_active, sm_active
    except ValueError:
        return None, None, None

# Function to calculate real-time FLOPS
def calculate_flops(sm_clock_hz, fp_active, sm_active, precision="FP32"):
    if sm_clock_hz is None or fp_active is None or sm_active is None:
        return None

    if precision == "FP32":
        factor = FP32_INSTRUCTIONS_PER_CYCLE
    elif precision == "FP64":
        factor = 1  # FP64 has lower throughput
    else:
        return None

    flops = sm_clock_hz * fp_active * sm_active * NUM_SMS * CUDA_CORES_PER_SM * factor
    return flops / 1e12  # Convert to TFLOPS

# Start monitoring
# print("Monitoring GPU Performance (Press Ctrl+C to stop)...")

# Write CSV header
with open(csv_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "SM Clock (MHz)", "FP32 Active", "FP64 Active", "SM Active", "FP32 FLOPS (TFLOPS)", "FP64 FLOPS (TFLOPS)"])

try:
    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Get metrics
        sm_clock_hz = get_sm_clock()
        fp32_active, fp64_active, sm_active = get_dcgm_metrics()

        # Compute FLOPS
        fp32_flops = calculate_flops(sm_clock_hz, fp32_active, sm_active, precision="FP32")
        fp64_flops = calculate_flops(sm_clock_hz, fp64_active, sm_active, precision="FP64")

        # Print output
        print(f"[{timestamp}] SM Clock: {sm_clock_hz / 1e6 if sm_clock_hz else 'N/A'} MHz | FP32: {fp32_flops:.2f} TFLOPS | FP64: {fp64_flops:.2f} TFLOPS")

        # Save to CSV
        with open(csv_filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, sm_clock_hz / 1e6 if sm_clock_hz else "N/A", fp32_active, fp64_active, sm_active, fp32_flops, fp64_flops])

        time.sleep(0.5)  # Update every second

except KeyboardInterrupt:
    print("\nMonitoring stopped. Data saved to", csv_filename)
