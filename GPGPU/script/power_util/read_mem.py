import time
import os
import csv
import argparse
import psutil
import subprocess
import re

# Function to run perf and capture IMC throughput
def monitor_imc_throughput(benchmark_pid, output_csv, interval=1.0):
    perf_cmd = [
        "perf", "stat", "-I", str(int(interval * 1000)),  # Report every interval seconds
        "-e", "uncore_imc_0/cas_count_read/", "-e", "uncore_imc_0/cas_count_write/",
        "-e", "uncore_imc_1/cas_count_read/", "-e", "uncore_imc_1/cas_count_write/",
        "-e", "uncore_imc_2/cas_count_read/", "-e", "uncore_imc_2/cas_count_write/",
        "-e", "uncore_imc_3/cas_count_read/", "-e", "uncore_imc_3/cas_count_write/",
        "-e", "uncore_imc_4/cas_count_read/", "-e", "uncore_imc_4/cas_count_write/",
        "-e", "uncore_imc_5/cas_count_read/", "-e", "uncore_imc_5/cas_count_write/",
        "-e", "uncore_imc_6/cas_count_read/", "-e", "uncore_imc_6/cas_count_write/",
        "-e", "uncore_imc_7/cas_count_read/", "-e", "uncore_imc_7/cas_count_write/",
        "-e", "uncore_imc_8/cas_count_read/", "-e", "uncore_imc_8/cas_count_write/",
        "-e", "uncore_imc_9/cas_count_read/", "-e", "uncore_imc_9/cas_count_write/",
        "-e", "uncore_imc_10/cas_count_read/", "-e", "uncore_imc_10/cas_count_write/",
        "-e", "uncore_imc_11/cas_count_read/", "-e", "uncore_imc_11/cas_count_write/",
    ]

    proc = subprocess.Popen(perf_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    start_time = time.time()
    throughput_data = []
    
    while psutil.pid_exists(benchmark_pid):
        time.sleep(interval)
        elapsed_time = time.time() - start_time
        total_reads = 0.0
        total_writes = 0.0

        for _ in range(24):
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
        total_mb = total_mib * 1.04858  # Convert MiB to MB
        throughput_data.append([elapsed_time, total_mb])

        # print(f"Memory Throughput: {total_mb:.2f} MB/s")
        
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time (s)', 'Memory Throughput (MB/s)'])
        writer.writerows(throughput_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor IMC throughput using perf.')
    parser.add_argument('--pid', type=int, help='PID of the benchmark process', required=True)
    parser.add_argument('--output_csv', type=str, help='Output CSV file path', required=True)
    args = parser.parse_args()
    
    monitor_imc_throughput(args.pid, args.output_csv)
