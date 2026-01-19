import subprocess
import csv
import os
import sys
from pathlib import Path

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
OUTPUT_FILE = f"data/gdb_normal_{BENCHMARK}.csv"

if not os.path.exists(TARGET_APP):
    print(f"Error: {TARGET_APP} not found.")
    print("Please compile: make all")
    sys.exit(1)

os.makedirs("data", exist_ok=True)

print("=" * 60)
print("GDB Normal Execution (NO bit-flip)")
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
        # GDB script WITHOUT bit-flip
        gdb_script = f"""
set pagination off
set confirm off
break main
run
next
next
next
continue
quit
"""
        
        script_file = Path("/tmp/gdb_normal.txt")
        script_file.write_text(gdb_script)
        
        # Run with perf
        cmd = f"perf stat -e {HPC_EVENTS} -x, gdb --batch -x {script_file} {TARGET_APP} 2>&1"
        
        try:
            result = subprocess.check_output(cmd, shell=True, timeout=5).decode('utf-8')
            
            # Parse perf output
            hpc_values = []
            for line in result.strip().split('\n'):
                parts = line.split(',')
                if len(parts) > 0:
                    val = parts[0].replace('<not counted>', '').replace('<not supported>', '').strip()
                    if val.isdigit():
                        hpc_values.append(val)
            
            if len(hpc_values) >= 4:
                writer.writerow(hpc_values[:4] + ["0"])  # label=0: normal
                success_count += 1
        
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass

        if i % 100 == 0:
            print(f"Progress: {i}/{TOTAL_RUNS} runs... (Collected: {success_count})")

print()
print("=" * 60)
print(f"✓ Done! Saved {success_count} samples to '{OUTPUT_FILE}'")
print("=" * 60)
