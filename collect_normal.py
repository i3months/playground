import subprocess
import csv
import os

TOTAL_RUNS = 1000
OUTPUT_FILE = "target_normal_hpc_data.csv"
TARGET_APP = "./target_app"
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

if not os.path.exists(TARGET_APP):
    print(f"Error: {TARGET_APP} not found. Please compile the C code first.")
    exit(1)

print(f"Starting normal data collection for {TARGET_APP}... (Total: {TOTAL_RUNS} runs)")

with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])

    for i in range(1, TOTAL_RUNS + 1):
        cmd = f"perf stat -e {HPC_EVENTS} -x, {TARGET_APP} 2>&1"
        
        try:
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            rows = result.strip().split('\n')
            data = []
            for row in rows:
                parts = row.split(',')
                if len(parts) > 0 and parts[0].isdigit():
                    data.append(parts[0])

            if len(data) == 4:
                writer.writerow(data + ["0"])
            
        except subprocess.CalledProcessError as e:
            print(f"Error during run {i}: {e}")

        if i % 100 == 0:
            print(f"Progress: {i}/{TOTAL_RUNS} runs completed...")

print(f"Success. Data saved to '{OUTPUT_FILE}'.")