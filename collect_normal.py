import subprocess
import csv
import os

# 1. Configuration for data collection
TOTAL_RUNS = 1000

# Update file name to distinguish from idle (sleep) data
OUTPUT_FILE = "target_normal_hpc_data.csv"

# Target application compiled from C code
TARGET_APP = "./target_app"

# Core HPC metrics identified as sensitive to faults in the Marvin paper
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

# 2. Check if the target application exists before starting
if not os.path.exists(TARGET_APP):
    print(f"Error: {TARGET_APP} not found. Please compile the C code first.")
    exit(1)

print(f"Starting normal data collection for {TARGET_APP}... (Total: {TOTAL_RUNS} runs)")

# 3. Open CSV file to record the microarchitectural baseline
with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    # Header: Metrics and Label (0 for normal)
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])

    for i in range(1, TOTAL_RUNS + 1):
        # Use 'perf stat' to measure the target application's execution
        # '-x,' provides output in CSV format for easier parsing
        cmd = f"perf stat -e {HPC_EVENTS} -x, {TARGET_APP} 2>&1"
        
        try:
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            # Parse the output string to extract numeric values
            rows = result.strip().split('\n')
            data = []
            for row in rows:
                parts = row.split(',')
                # Check if the first column is a digit (the metric value)
                if len(parts) > 0 and parts[0].isdigit():
                    data.append(parts[0])

            # Save the data if all 4 metrics are successfully collected
            if len(data) == 4:
                # Label '0' indicates a golden run (no fault injected)
                writer.writerow(data + ["0"])
            
        except subprocess.CalledProcessError as e:
            print(f"Error during run {i}: {e}")

        # Progress tracking
        if i % 100 == 0:
            print(f"Progress: {i}/{TOTAL_RUNS} runs completed...")

print(f"Success. Data saved to '{OUTPUT_FILE}'.")