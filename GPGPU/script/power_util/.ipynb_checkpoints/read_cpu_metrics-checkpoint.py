import time
import csv
import argparse
import psutil
import subprocess
import re
import threading

# Function to collect instructions per second
def collect_instructions():
    output = subprocess.run(
        ["perf", "stat", "-e", "instructions", "-a", "--field-separator=','", "-x", ",", "sleep", "1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    lines = output.stderr.strip().split("\n")
    instructions_line = next((line for line in lines if "instructions" in line), None)
    return instructions_line.split(",")[0] if instructions_line else "0"

# New function to collect LLC misses
def collect_llc_misses():
    output = subprocess.run(
        ["perf", "stat", "-e", "LLC-misses", "-a", "--field-separator=','", "-x", ",", "sleep", "1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    lines = output.stderr.strip().split("\n")
    llc_line = next((line for line in lines if "LLC-misses" in line), None)
    return llc_line.split(",")[0] if llc_line else "0"

# Function to monitor IPS in a thread
def monitor_ips(benchmark_pid, ips_data, interval=1.0):
    start_time = time.time()
    while psutil.pid_exists(benchmark_pid):
        elapsed_time = time.time() - start_time
        instructions_per_second = collect_instructions()
        ips_data.append([elapsed_time, instructions_per_second])
        time.sleep(0.01)

# New function to monitor LLC misses in a thread
def monitor_llc(benchmark_pid, llc_data, interval=1.0):
    start_time = time.time()
    while psutil.pid_exists(benchmark_pid):
        elapsed_time = time.time() - start_time
        llc_misses = collect_llc_misses()
        llc_data.append([elapsed_time, llc_misses])
        time.sleep(0.01)

# Function to monitor IMC throughput in a thread (unchanged)
def monitor_imc_throughput(benchmark_pid, throughput_data, interval=1.0):
    perf_cmd = [
        "perf", "stat", "-I", str(int(interval * 1000)),
        "-e", "uncore_imc_0/cas_count_read/", "-e", "uncore_imc_0/cas_count_write/",
        "-e", "uncore_imc_1/cas_count_read/", "-e", "uncore_imc_1/cas_count_write/",
        "-e", "uncore_imc_2/cas_count_read/", "-e", "uncore_imc_2/cas_count_write/",
        "-e", "uncore_imc_3/cas_count_read/", "-e", "uncore_imc_3/cas_count_write/",
        "-e", "uncore_imc_4/cas_count_read/", "-e", "uncore_imc_4/cas_count_write/",
        "-e", "uncore_imc_5/cas_count_read/", "-e", "uncore_imc_5/cas_count_write/",
        "-e", "uncore_imc_6/cas_count_read/", "-e", "uncore_imc_6/cas_count_write/",
        "-e", "uncore_imc_7/cas_count_read/", "-e", "uncore_imc_7/cas_count_write/",
    ]
    proc = subprocess.Popen(perf_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    start_time = time.time()
    while psutil.pid_exists(benchmark_pid):
        time.sleep(0.01)
        elapsed_time = time.time() - start_time
        total_reads = 0.0
        total_writes = 0.0
        for _ in range(16):
            line = proc.stderr.readline()
            match = re.search(r"([\d\.]+)\s+MiB\s+uncore_imc_\d+/cas_count_(read|write)/", line)
            if match:
                value = float(match.group(1))
                event_type = match.group(2)
                if event_type == "read":
                    total_reads += value
                else:
                    total_writes += value
        total_mib = total_reads + total_writes
        total_mb = total_mib * 1.04858
        throughput_data.append([elapsed_time, total_mb])

# Function to synchronize data and write to CSV
def write_synchronized_data(output_csv, ips_data, throughput_data, llc_data):
    # Use the minimum length across all data lists
    min_length = min(len(ips_data), len(throughput_data), len(llc_data))
    ips_data = ips_data[:min_length]
    throughput_data = throughput_data[:min_length]
    llc_data = llc_data[:min_length]
    
    with open(output_csv, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "IPS", "Memory Throughput (MB/s)", "LLC Misses"])
        for i in range(min_length):
            writer.writerow([ips_data[i][0], ips_data[i][1], throughput_data[i][1], llc_data[i][1]])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor IPS, IMC throughput, and LLC misses concurrently.")
    parser.add_argument("--pid", type=int, help="PID of the benchmark process", required=True)
    parser.add_argument("--output_csv", type=str, help="Output CSV file path", required=True)
    args = parser.parse_args()

    ips_data = []
    throughput_data = []
    llc_data = []

    # Create three monitoring threads
    t1 = threading.Thread(target=monitor_ips, args=(args.pid, ips_data))
    t2 = threading.Thread(target=monitor_imc_throughput, args=(args.pid, throughput_data))
    t3 = threading.Thread(target=monitor_llc, args=(args.pid, llc_data))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    # Write the synchronized data to CSV
    write_synchronized_data(args.output_csv, ips_data, throughput_data, llc_data)
