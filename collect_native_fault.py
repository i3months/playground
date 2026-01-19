import subprocess
import csv
import os
import time

# --- Configuration ---
TOTAL_RUNS = 1000
OUTPUT_FILE = "faulty_hpc_native.csv"  # Native injector data
INJECTOR = "./simple_injector"
TARGET_APP = "./target_app"
# Marvin Paper Targets
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

# Check if binaries exist
if not os.path.exists(INJECTOR) or not os.path.exists(TARGET_APP):
    print("Error: 'simple_injector' or 'target_app' not found.")
    print("Please compile them first using GCC.")
    exit(1)

print(f"Starting Native Fault Injection (Marvin Style)... (Total: {TOTAL_RUNS})")
print(f"Output will be saved to: {OUTPUT_FILE}")

with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    # Header: HPC metrics + Label (1 for Fault)
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])

    success_count = 0

    for i in range(1, TOTAL_RUNS + 1):
        # Command: perf stat -> simple_injector -> target_app
        # -x, : Output in CSV format for easier parsing
        # 2>&1 : Redirect stderr (where perf writes) to stdout
        cmd = f"sudo perf stat -e {HPC_EVENTS} -x, {INJECTOR} {TARGET_APP} 2>&1"
        
        try:
            # Run the command
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            # Parse perf output
            # perf with -x, looks like: "12345,,cycles,..."
            rows = result.strip().split('\n')
            data_row = []
            
            for line in rows:
                parts = line.split(',')
                # Filter out lines that are not HPC data (e.g., injector logs)
                if len(parts) > 2 and parts[0].isdigit(): 
                    # Marvin focuses on the raw counter values
                    data_row.append(parts[0]) 

            # Only save if we captured all 4 metrics
            if len(data_row) == 4:
                writer.writerow(data_row + ["1"]) # Label 1 for Fault
                success_count += 1
            
        except subprocess.CalledProcessError:
            # Fault injection can sometimes crash the process violently
            pass
        except Exception as e:
            print(f"Error at run {i}: {e}")

        # Progress Log
        if i % 100 == 0:
            print(f"Progress: {i}/{TOTAL_RUNS} runs... (Collected: {success_count})")

print(f"\nDone. Saved {success_count} valid samples to '{OUTPUT_FILE}'.")