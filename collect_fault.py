import subprocess
import csv
import os
import random
import sys

# ============================================
# Configuration
# ============================================
TOTAL_RUNS = 1000
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

# 벤치마크 선택 (명령줄 인자 또는 기본값)
if len(sys.argv) > 1:
    BENCHMARK = sys.argv[1]
else:
    BENCHMARK = "target"  # 기본값

# 벤치마크별 설정
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
OUTPUT_FILE = f"data/faulty_{BENCHMARK}_gdb.csv"
TARGET_REGISTERS = ["x0", "x1", "x2", "x3", "x4", "x5"]

if not os.path.exists(TARGET_APP):
    print(f"Error: {TARGET_APP} not found.")
    print("Please compile: make all")
    sys.exit(1)

os.makedirs("data", exist_ok=True)

print("=" * 60)
print("GDB Fault Injection")
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
        reg = random.choice(TARGET_REGISTERS)
        bit = random.randint(0, 63)
        
        gdb_cmd = (
            f"gdb --batch "
            f"-ex 'break main' "
            f"-ex 'run' "
            f"-ex 'next' "
            f"-ex 'next' "
            f"-ex 'next' "
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

print()
print("=" * 60)
print(f"✓ Success! Faulty data saved to '{OUTPUT_FILE}'")
print("=" * 60)