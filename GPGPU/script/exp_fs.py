import os
import subprocess
import time
import signal
import argparse
import csv
import pandas as pd


# Define paths and executables
home_dir = os.path.expanduser('~')
python_executable = subprocess.getoutput('which python3')  # Adjust based on your Python version

# scripts for CPU, GPU power monitoring
read_cpu_power = "./power_util/read_cpu_power.py"
read_gpu_power = "./power_util/read_gpu_power.py"

# scritps for running various benchmarks
run_altis = "./run_benchmark/run_altis.py"
run_ecp = "./run_benchmark/run_ecp.py"

# Define your benchmarks, for testing replace the list with just ['FT'] for example
# ecp_benchmarks = ['FT', 'CG', 'LULESH', 'Nekbone', 'AMG2013', 'miniFE']
ecp_benchmarks = ['XSBench','miniGAN','CRADL','sw4lite','Laghos']
ecp_benchmarks = ['miniGAN','CRADL','sw4lite','Laghos']

altis_benchmarks_0 = ['busspeeddownload','busspeedreadback','maxflops']
altis_benchmarks_1 = ['bfs','gemm','gups','pathfinder','sort']
altis_benchmarks_2 = ['cfd','cfd_double','fdtd2d','kmeans','lavamd',
                      'nw','particlefilter_float','particlefilter_naive','raytracing',
                      'srad','where']


altis_benchmarks_0 = ['busspeeddownload']
altis_benchmarks_1 = ['pathfinder','sort','gemm']
altis_benchmarks_2 = ['cfd_double','kmeans','lavamd','fdtd2d',
                     'particlefilter_naive','raytracing']



# cpu_caps = [65,70,75,80,85,90,95,100,105,110,115,120,125]

# gpu_caps = [260, 240, 220, 200, 180, 160, 140, 120, 100]
# cpu_caps = [105, 100, 95, 90, 85, 80, 75, 70, 65]
cpu_caps = [105]
gpu_fs_ls = [2100, 2025, 1935, 1845, 1755, 1665, 1575, 1485, 1395, 1305, 1215, 1125, 1035, 945, 855, 765, 675, 585, 495, 405, 315]





# Setup environment
modprobe_command = "sudo modprobe msr"
sysctl_command = "sudo sysctl -n kernel.perf_event_paranoid=-1"

subprocess.run(modprobe_command, shell=True)
subprocess.run(sysctl_command, shell=True)



def run_benchmark(benchmark_script_dir,benchmark, suite, test):

    # store avg power data 
    tmp_cpu = f"../data/{suite}_fs_res/tmp_cpu.csv"
    tmp_gpu = f"../data/{suite}_fs_res/tmp_gpu.csv"

    def cap_exp(cpu_cap, gpu_fs, output_file):
        
        # Set CPU and GPU power caps and wait for them to take effect
        subprocess.run([f"./power_util/cpu_cap.sh {cpu_cap}"], shell=True)
        subprocess.run([f"./power_util/gpu_fs.sh {gpu_fs}"], shell=True)
        time.sleep(2)  # Wait for the power caps to take effect
    
        # Run the benchmark
        start = time.time()
        if suite == "altis":
            run_benchmark_command = f"{python_executable} {run_altis} --benchmark {benchmark} --benchmark_script_dir {os.path.join(home_dir, benchmark_script_dir)}"
        elif suite == "ecp":
            run_benchmark_command = f"{python_executable} {run_ecp} --benchmark {benchmark} --benchmark_script_dir {os.path.join(home_dir, benchmark_script_dir)}"
        
        benchmark_process = subprocess.Popen(run_benchmark_command, shell=True)
        benchmark_pid = benchmark_process.pid

        # Start CPU power monitoring, passing the PID of the benchmark process
        monitor_command_cpu = f"echo 9900 | sudo -S {python_executable} {read_cpu_power}  --output_csv {tmp_cpu} --pid {benchmark_pid} --avg 1"
        monitor_process = subprocess.Popen(monitor_command_cpu, shell=True, stdin=subprocess.PIPE, text=True)
    
        # Start GPU power monitoring, passing the PID of the benchmark process
        monitor_command_gpu = f"echo 9900 | sudo -S {python_executable} {read_gpu_power}  --output_csv {tmp_gpu} --pid {benchmark_pid} --avg 1"
        monitor_process = subprocess.Popen(monitor_command_gpu, shell=True, stdin=subprocess.PIPE, text=True)
    
            
        benchmark_process.wait()  # Wait for the benchmark to complete
        end = time.time()
        runtime = round(end - start, 2)
    
        # Check if the output file exists to decide whether to write headers
        file_exists = os.path.isfile(output_file)

        time.sleep(2)
        # read CPU and GPU energy 
        tmp_cpu_df = pd.read_csv(tmp_cpu)
        tmp_gpu_df = pd.read_csv(tmp_gpu)
        cpu_e = tmp_cpu_df.iloc[0, 0] 
        gpu_e = tmp_gpu_df.iloc[0, 0]
        os.remove(tmp_cpu)
        os.remove(tmp_gpu)

        # Write data to the output file
        with open(output_file, 'a', newline='') as file:  # Open file in append mode
            writer = csv.writer(file)
            if not file_exists:  # If file doesn't exist, write the header
                writer.writerow(['CPU Cap (W)', 'GPU F (MHz)','CPU_E (J)','GPU_E (J)','Runtime (s)'])
            # Write the new data row
            writer.writerow([cpu_cap, gpu_fs, cpu_e, gpu_e, runtime])
            
        
        
################## end helper function ####################
    
    if not test:
        output_file_cpu = f"../data/{suite}_fs_res/{benchmark}_cap_cpu.csv"
        output_file_gpu = f"../data/{suite}_fs_res/{benchmark}_cap_gpu.csv"
        output_file_dual = f"../data/{suite}_fs_res/{benchmark}_cap_dual.csv"
    else:
        output_file = f"../data/{suite}_test/{benchmark}_cap.csv"

    
   
    
    # # CPU cap only 
    # for cpu_cap in cpu_caps:
    #     gpu_cap = gpu_caps[-1]
    #     cap_exp(cpu_cap, gpu_cap, output_file_cpu)
       

    # # GPU cap only
    # for gpu_cap in gpu_caps:
    #     cpu_cap = cpu_caps[-1]
    #     cap_exp(cpu_cap, gpu_cap, output_file_gpu)
        


    
    #dual cap
    for cpu_cap in cpu_caps:
        for gpu_fs in gpu_fs_ls:
            cap_exp(cpu_cap, gpu_fs, output_file_dual)


    subprocess.run([f"./power_util/gpu_fs.sh 2100"], shell=True)


if __name__ == "__main__":
   # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run benchmarks and monitor power consumption.')
    parser.add_argument('--benchmark', type=str, help='Optional name of the benchmark to run', default=None)
    parser.add_argument('--test', type=int, help='whether it is a test run', default=None)
    parser.add_argument('--suite', type=int, help='0 for ECP, 1 for ALTIS, 2 for all', default=1)

    args = parser.parse_args()
    benchmark = args.benchmark
    test = args.test
    suite = args.suite


    if suite == 0 or suite ==2:
        benchmark_script_dir = f"power/script/run_benchmark/ecp_script"
        # single test
        if benchmark:
            run_benchmark(benchmark_script_dir, benchmark,"ecp",test)
        # run all ecp benchmarks
        else:
            for benchmark in ecp_benchmarks:
                run_benchmark(benchmark_script_dir, benchmark,"ecp",test)
    

    if suite == 1 or suite ==2:
        # Map of benchmarks to their paths
        benchmark_paths = {
            "level0": altis_benchmarks_0,
            "level1": altis_benchmarks_1,
            "level2": altis_benchmarks_2
        }
    
        if benchmark:
            # Find which level the input benchmark belongs to
            found = False
            for level, benchmarks in benchmark_paths.items():
                if benchmark in benchmarks:
                    benchmark_script_dir = f"power/script/run_benchmark/altis_script/{level}"
                    run_benchmark(benchmark_script_dir, benchmark,"altis",test)
                    found = True
                    break
        else:
    
            for benchmark in altis_benchmarks_0:
                benchmark_script_dir = "power/script/run_benchmark/altis_script/level0"
                run_benchmark(benchmark_script_dir, benchmark,"altis",test)
            
            
            for benchmark in altis_benchmarks_1:
                benchmark_script_dir = "power/script/run_benchmark/altis_script/level1"
                run_benchmark(benchmark_script_dir, benchmark,"altis",test)
            
            
            for benchmark in altis_benchmarks_2:
                benchmark_script_dir = "power/script/run_benchmark/altis_script/level2"
                run_benchmark(benchmark_script_dir, benchmark,"altis",test)