import subprocess
import csv
import os
import sys

TOTAL_RUNS = 3000
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

if len(sys.argv) > 1:
    BENCHMARK = sys.argv[1]
else:
    BENCHMARK = "basicmath"

TARGET_APP = "./basicmath_bench_fi"
OUTPUT_NORMAL = f"data/software_normal_{BENCHMARK}.csv"
OUTPUT_FAULT = f"data/software_fault_{BENCHMARK}.csv"

if not os.path.exists(TARGET_APP):
    print(f"Error: {TARGET_APP} not found.")
    print("Please compile: gcc -DBENCHMARK=1 example_benchmark_with_fi.c -o basicmath_bench_fi -lm")
    sys.exit(1)

os.makedirs("data", exist_ok=True)

print("=" * 60)
print("Software-based Fault Injection")
print("=" * 60)
print(f"Benchmark: {BENCHMARK}")
print(f"Target: {TARGET_APP}")
print(f"Total runs: {TOTAL_RUNS} × 2 (Normal + Fault)")
print("=" * 60)
print()

# Normal 데이터 수집
print("Collecting Normal data...")
with open(OUTPUT_NORMAL, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])
    
    for i in range(1, TOTAL_RUNS + 1):
        # ENABLE_FAULT=0 (Normal)
        cmd = f"ENABLE_FAULT=0 perf stat -e {HPC_EVENTS} -x, {TARGET_APP} 2>&1"
        
        try:
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            rows = result.strip().split('\n')
            data_row = []
            
            for line in rows:
                parts = line.split(',')
                if len(parts) > 2 and parts[0].isdigit():
                    data_row.append(parts[0])
            
            if len(data_row) == 4:
                writer.writerow(data_row + ["0"])
        
        except:
            pass
        
        if i % 100 == 0:
            print(f"  Progress: {i}/{TOTAL_RUNS}")

print(f"✓ Normal data saved to {OUTPUT_NORMAL}")

# Fault 데이터 수집
print("\nCollecting Fault data...")
with open(OUTPUT_FAULT, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])
    
    for i in range(1, TOTAL_RUNS + 1):
        # ENABLE_FAULT=1 (Fault)
        cmd = f"ENABLE_FAULT=1 perf stat -e {HPC_EVENTS} -x, {TARGET_APP} 2>&1"
        
        try:
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            rows = result.strip().split('\n')
            data_row = []
            
            for line in rows:
                parts = line.split(',')
                if len(parts) > 2 and parts[0].isdigit():
                    data_row.append(parts[0])
            
            if len(data_row) == 4:
                writer.writerow(data_row + ["1"])
        
        except:
            pass
        
        if i % 100 == 0:
            print(f"  Progress: {i}/{TOTAL_RUNS}")

print(f"✓ Fault data saved to {OUTPUT_FAULT}")
print("\n" + "=" * 60)
print("Data collection completed!")
print("=" * 60)
