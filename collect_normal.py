import subprocess
import csv
import os
import sys

# ============================================
# Configuration
# ============================================
TOTAL_RUNS = 3000  # 적당한 개수
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
OUTPUT_FILE = f"data/normal_{BENCHMARK}.csv"

if not os.path.exists(TARGET_APP):
    print(f"Error: {TARGET_APP} not found. Please compile first: make all")
    sys.exit(1)

os.makedirs("data", exist_ok=True)

print("=" * 60)
print(f"Normal Data Collection")
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

print()
print("=" * 60)
print(f"✓ Success! Data saved to '{OUTPUT_FILE}'")
print("=" * 60)