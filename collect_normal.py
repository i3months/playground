import subprocess
import csv
import time

# Collect Count
TOTAL_RUNS = 1000
# File Name
output_file = "normal_hpc_data.csv"

# Set HPC Metric
events = "cycles,instructions,cache-misses,branch-misses"

print(f"Normal Data Collect Start... {TOTAL_RUNS} Count...")

with open(output_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    # [Metric Name + Label]
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])

    for i in range(1, TOTAL_RUNS + 1):
        # perf stat (csv)
        cmd = f"perf stat -e {events} -x, sleep 0.1 2>&1"
        result = subprocess.check_output(cmd, shell=True).decode('utf-8')

        rows = result.strip().split('\n')
        data = []
        for row in rows:
            parts = row.split(',')
            if len(parts) > 0 and parts[0].isdigit():
                data.append(parts[0])

        if len(data) == 4:
            writer.writerow(data + ["0"])
            
        if i % 100 == 0:
            print(f"{i}/{TOTAL_RUNS} Count...")

print(f"Finish.. '{output_file}' File Check...")