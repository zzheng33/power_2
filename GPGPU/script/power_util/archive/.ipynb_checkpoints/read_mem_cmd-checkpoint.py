import subprocess
import re

# Define the perf command to collect IMC throughput every 10 seconds
perf_cmd = [
    "perf", "stat", "-I", "1000",  # Report every 10 seconds
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
    "sleep", "999999"
]

# Run perf as a background process
proc = subprocess.Popen(perf_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

try:
    while True:
        # Reset total throughput counters for this interval
        total_reads = 0.0
        total_writes = 0.0

        # Read perf output for one interval
        for _ in range(24):  
            line = proc.stderr.readline()

            # Match lines containing throughput values (e.g., "0.02 MiB uncore_imc_0/cas_count_read/")
            match = re.search(r"([\d\.]+)\s+MiB\s+uncore_imc_\d+/cas_count_(read|write)/", line)

            if match:
                value = float(match.group(1))  # Extract throughput value in MiB
                event_type = match.group(2)  # Determine if it's a read or write event

                # Sum throughput over all IMCs
                if event_type == "read":
                    total_reads += value
                else:
                    total_writes += value

        # Convert MiB to MB (optional)
        total_mib = total_reads + total_writes
        total_mb = total_mib * 1.04858  # 1 MiB = 1.04858 MB

        # Print total bandwidth for this interval
        print(f"Memory Throughput: {total_mb:.2f} MB/s")

except KeyboardInterrupt:
    print("Stopping monitoring...")
    proc.terminate()
