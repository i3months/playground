import subprocess
import csv
import os
import sys

# ============================================
# Configuration
# ============================================
TOTAL_RUNS = 3000  
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

if len(sys.argv) > 1:
    BENCHMARK = sys.argv[1]
else:
    BENCHMARK = "basicmath"

BENCHMARKS = {
    "basicmath": "./basicmath_bench",
    "qsort": "./qsort_bench",
    "sha": "./sha_bench",
    "target": "./target_app"
}

if BENCHMARK not in BENCHMARKS:
    print(f"Error: Unknown benchmark '{BENCHMARK}'")
    print(f"Available: {', '.join(BENCHMARKS.keys())}")
    sys.exit(1)

TARGET_APP = BENCHMARKS[BENCHMARK]
OUTPUT_FILE = f"data/ptrace_normal_{BENCHMARK}.csv"
RUNNER = "./simple_runner_fast"  # Fast version!

# Check if binaries exist
if not os.path.exists(RUNNER) or not os.path.exists(TARGET_APP):
    print(f"Error: '{RUNNER}' or '{TARGET_APP}' not found.")
    print("Please compile: make all")
    sys.exit(1)

os.makedirs("data", exist_ok=True)

print("=" * 60)
print("Ptrace Normal Execution (with ptrace overhead)")
print("=" * 60)
print(f"Benchmark: {BENCHMARK}")
print(f"Target: {TARGET_APP}")
print(f"Total runs: {TOTAL_RUNS}")
print(f"Output: {OUTPUT_FILE}")
print("=" * 60)
print()

with open(OUTPUT_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])

    success_count = 0

    for i in range(1, TOTAL_RUNS + 1):
        # Run with ptrace (NO fault injection)
        cmd = f"sudo perf stat -e {HPC_EVENTS} -x, {RUNNER} {TARGET_APP} 2>&1"
        
        try:
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            # Parse perf output
            rows = result.strip().split('\n')
            data_row = []
            
            for line in rows:
                parts = line.split(',')
                if len(parts) > 2 and parts[0].isdigit(): 
                    data_row.append(parts[0]) 

            # Only save if we captured all 4 metrics
            if len(data_row) == 4:
                writer.writerow(data_row + ["0"])  # label=0: normal
                success_count += 1
            
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            print(f"Error at run {i}: {e}")

        # Progress Log
        if i % 100 == 0:
            print(f"Progress: {i}/{TOTAL_RUNS} runs... (Collected: {success_count})")

print()
print("=" * 60)
print(f"✓ Done! Saved {success_count} valid samples to '{OUTPUT_FILE}'")
print("=" * 60)
