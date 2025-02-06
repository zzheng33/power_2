#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <stdbool.h>
#include <sys/stat.h>
#include <stdint.h>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <errno.h>


int dual_cap = 0;
double step = 0.1;
double current_uf1 = 2.2;
double current_uf2 = 2.2;
int init = 2.2;
int max_uf = 2.2;
int min_uf = 0.8;
int low_ts = 10;
int high_ts = 90

typedef struct {
    double time_sec;
    double utilization;
} cpu_sample;


void SoC(util) {
   // if util < 10%, set the uf to 0.8
    if (util <= low_ts) {
        if (dual_cap==1){
            current_uf1 = 0.8;
            current_uf2 = 0.8;
            char command[128];
            snprintf(command, sizeof(command), "sudo /home/cc/power/GPGPU/script/power_util/set_uncore_freq.sh %.2f %.2f", min_uf, min_uf);
            (void)system(command);
        }
        else{
            current_uf1 = 0.8;
            current_uf2 = 2.2;
            char command[128];
            snprintf(command, sizeof(command), "sudo /home/cc/power/GPGPU/script/power_util/set_uncore_freq.sh %.2f %.2f", min_uf, max_uf);
            (void)system(command);
        }
    }
    // if util >= 90%, increment the current uf by 0.1 GHz
    else if (util >= high_ts) {
        if (dual_cap==1){
            if (current_uf1<max_uf) current_uf1 +=step;
            if (current_uf2<max_uf) current_uf2 +=step;
            char command[128];
            snprintf(command, sizeof(command), "sudo /home/cc/power/GPGPU/script/power_util/set_uncore_freq.sh %.2f %.2f", current_uf1, current_uf2);
            (void)system(command);
        }
        else{
            if (current_uf1<max_uf) current_uf1 +=step;
            char command[128];
            snprintf(command, sizeof(command), "sudo /home/cc/power/GPGPU/script/power_util/set_uncore_freq.sh %.2f %.2f", current_uf1, current_uf2);
            (void)system(command);
        }
    }
}


void monitor_cpu_util(int pid, const char *output_csv, double interval) {
    // Initial capacity for data storage
    size_t capacity = 100000;
    size_t count = 0;
    cpu_sample *data = malloc(capacity * sizeof(cpu_sample));
    if (!data) {
        perror("malloc failed");
        exit(EXIT_FAILURE);
    }

    struct timespec start_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    // Variables to hold previous CPU stats
    unsigned long long prev_idle = 0, prev_total = 0;

    while (kill(pid, 0) == 0) {
        struct timespec current_time;
        clock_gettime(CLOCK_MONOTONIC, &current_time);

        double elapsed_time_ms = (current_time.tv_sec - start_time.tv_sec) * 1000.0
                                 + (current_time.tv_nsec - start_time.tv_nsec) / 1e6;
        double elapsed_time_sec = elapsed_time_ms / 1000.0;

        // Read /proc/stat
        FILE *fp = fopen("/proc/stat", "r");
        if (!fp) {
            perror("Error reading /proc/stat");
            free(data);
            exit(EXIT_FAILURE);
        }

        char line[256];
        unsigned long long user, nice, system, idle, iowait, irq, softirq, steal;
        if (fgets(line, sizeof(line), fp)) {
            sscanf(line, "cpu %llu %llu %llu %llu %llu %llu %llu %llu",
                   &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal);
        }
        fclose(fp);

        // Calculate total CPU time and idle time
        unsigned long long total = user + nice + system + idle + iowait + irq + softirq + steal;
        unsigned long long idle_time = idle + iowait;

        // Calculate CPU utilization
        double cpu_usage = 0.0;
        if (prev_total != 0) {
            unsigned long long total_diff = total - prev_total;
            unsigned long long idle_diff = idle_time - prev_idle;
            cpu_usage = 100.0 * (1.0 - ((double) idle_diff / total_diff));
        }

        // Update previous values
        prev_idle = idle_time;
        prev_total = total;

        // Store the sample
        if (count == capacity) {
            capacity *= 2;
            cpu_sample *new_data = realloc(data, capacity * sizeof(cpu_sample));
            if (!new_data) {
                perror("realloc failed");
                free(data);
                exit(EXIT_FAILURE);
            }
            data = new_data;
        }

        data[count].time_sec = elapsed_time_sec;
        data[count].utilization = cpu_usage;
        count++;


        SoC(cpu_usage);
        // Sleep for the desired interval
        usleep((useconds_t)(interval * 1e6));
    }

    // Write all collected data to CSV
    FILE *fp_out = fopen(output_csv, "w");
    if (fp_out == NULL) {
        perror("Error opening CSV file");
        free(data);
        exit(EXIT_FAILURE);
    }

    // Write header
    fprintf(fp_out, "time,utilization\n");

    // Write each sample
    for (size_t i = 0; i < count; i++) {
        fprintf(fp_out, "%.2f,%.2f\n", data[i].time_sec, data[i].utilization);
    }

    fclose(fp_out);
    free(data);
}


int main(int argc, char *argv[]) {
    int pid = -1;
    const char *output_csv = NULL;
    double interval = 0.2;

    // Check if the arguments are in the form --param=value
    for (int i = 1; i < argc; i++) {
        if (strncmp(argv[i], "--pid=", 6) == 0) {
            pid = atoi(argv[i] + 6);
        } else if (strncmp(argv[i], "--output_csv=", 13) == 0) {
            output_csv = argv[i] + 13;
        } else if (strncmp(argv[i], "--dual_cap=", 11) == 0) {
            dual_cap = atoi(argv[i] + 11);
        } else {
            fprintf(stderr, "Unknown argument: %s\n", argv[i]);
            exit(EXIT_FAILURE);
        }
    }

    // Check if the required arguments were provided
    if (pid == -1 || output_csv == NULL) {
        fprintf(stderr, "Usage: %s --pid=<PID> --output_csv=<output_csv>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    monitor_cpu_util(pid, output_csv, interval);

    return 0;
}