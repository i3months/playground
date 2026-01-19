import subprocess
import csv
import os
import random

TOTAL_RUNS = 1000
OUTPUT_FILE = "faulty_hpc_data.csv"
TARGET_APP = "./target_app"
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

TARGET_REGISTERS = ["x0", "x1", "x2", "x3", "x4", "x5"]

if not os.path.exists(TARGET_APP):
    print(f"Error: {TARGET_APP} not found.")
    exit(1)

print(f"Starting faulty data collection (Bit-Flip via GDB)... (Total: {TOTAL_RUNS} runs)")

with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])

    for i in range(1, TOTAL_RUNS + 1):
        reg = random.choice(TARGET_REGISTERS)
        bit = random.randint(0, 63)
        
        gdb_cmd = (
            f"gdb --batch "
            f"-ex 'break target_app.c:10' "
            f"-ex 'run' "
            f"-ex 'set ${reg} = ${reg} ^ (1ULL << {bit})' "
            f"-ex 'continue' "
            f"--args {TARGET_APP}"
        )

        perf_cmd = f"perf stat -e {HPC_EVENTS} -x, {gdb_cmd} 2>&1"
        
        try:
            result = subprocess.check_output(perf_cmd, shell=True).decode('utf-8')
            
            rows = result.strip().split('\n')
            data = []
            for row in rows:
                parts = row.split(',')
                if len(parts) > 0 and parts[0].isdigit():
                    data.append(parts[0])

            if len(data) == 4:
                writer.writerow(data + ["1"])
            
        except subprocess.CalledProcessError as e:
            print(f"Run {i}: Program crashed or error occurred due to fault injection.")

        if i % 100 == 0:
            print(f"Progress: {i}/{TOTAL_RUNS} runs completed...")

print(f"Success. Faulty data saved to '{OUTPUT_FILE}'.")