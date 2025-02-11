import time
import os
import csv
import argparse
import psutil
import subprocess  
import pandas as pd

# Function to collect instruction count data
def collect_instructions():
    output = subprocess.run(
        ["perf", "stat", "-e", "instructions", "-a", "--field-separator=','", "-x", ",", "sleep", "1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    lines = output.stderr.strip().split("\n")  # Read stderr and split lines
    instructions_line = next((line for line in lines if "instructions" in line), None)
    instructions = instructions_line.split(",")[0]  # Extract first value (instruction count)

    return instructions


# Function to continuously monitor instructions per second
def monitor_instructions(benchmark_pid, output_csv):
    start_time = time.time()
    performance_data = []
    
    while psutil.pid_exists(benchmark_pid):
        elapsed_time = time.time() - start_time
        instructions_per_second = collect_instructions()
        performance_data.append([elapsed_time, instructions_per_second])
        # time.sleep(1)
    
    with open(output_csv, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "IPS"])
        writer.writerows(performance_data)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor CPU instructions per second.')
    parser.add_argument('--pid', type=int, help='PID of the benchmark process', required=True)
    parser.add_argument('--output_csv', type=str, help='Output CSV file path')
    args = parser.parse_args()
    monitor_instructions(args.pid, args.output_csv)
