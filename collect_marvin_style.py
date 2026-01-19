import subprocess
import csv
import os
import random
import sys
from pathlib import Path

# ============================================
# Configuration (Marvin-style)
# ============================================
TOTAL_FAULTS = 1000  # Number of different faults
NUM_RUNS_PER_FAULT = 7  # Marvin's num_of_run
HPC_EVENTS = "cycles,instructions,cache-misses,branch-misses"

# 벤치마크 선택 (명령줄 인자 또는 기본값)
if len(sys.argv) > 1:
    BENCHMARK = sys.argv[1]
else:
    BENCHMARK = "basicmath"  # 기본값

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
OUTPUT_FILE = f"data/faulty_{BENCHMARK}_marvin.csv"
LOG_FILE = f"data/fault_log_{BENCHMARK}_marvin.txt"

# Fault injection parameters
TARGET_REGISTERS = ["x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7"]

# ============================================
# Helper Functions
# ============================================

def bit_flip_value(value, bit_pos):
    """Perform bit-flip at specified position (Marvin's bitFlipping)"""
    return value ^ (1 << bit_pos)


def inject_fault_gdb(target_reg, bit_pos):
    """
    Inject fault using GDB (similar to Marvin's fault_injection)
    Returns: (success, hpc_data)
    """
    # Create GDB script for fault injection
    gdb_script = f"""
set pagination off
set confirm off
break main
run
next
next
next
set ${target_reg} = ${target_reg} ^ (1ULL << {bit_pos})
continue
quit
"""
    
    script_file = Path("/tmp/gdb_inject_marvin.txt")
    script_file.write_text(gdb_script)
    
    # Run with perf (Marvin's HPC collection)
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
                    hpc_values.append(int(val))
        
        if len(hpc_values) >= 4:
            return True, hpc_values[:4]
        else:
            return False, None
    
    except subprocess.TimeoutExpired:
        return False, None  # Crash/hang
    except Exception as e:
        return False, None


def classify_outcome(hpc_samples, expected_runs):
    """
    Classify fault outcome (Marvin's classification)
    - benign: All runs completed successfully
    - crash: Program crashed/hung
    - SDC: Some runs failed (Silent Data Corruption)
    """
    if len(hpc_samples) == 0:
        return "crash"
    elif len(hpc_samples) == expected_runs:
        return "benign"
    else:
        return "SDC"


# ============================================
# Main Collection Function
# ============================================

def main():
    print("=" * 60)
    print("Marvin-style Fault Injection Data Collection")
    print("=" * 60)
    print(f"Benchmark: {BENCHMARK}")
    print(f"Target: {TARGET_APP}")
    print(f"Total faults: {TOTAL_FAULTS}")
    print(f"Runs per fault: {NUM_RUNS_PER_FAULT}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Log: {LOG_FILE}")
    print("=" * 60)
    print()
    
    # Check if target exists
    if not os.path.exists(TARGET_APP):
        print(f"Error: {TARGET_APP} not found.")
        print("Please compile: make all")
        sys.exit(1)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Open output files
    csv_file = open(OUTPUT_FILE, mode='w', newline='')
    log_file = open(LOG_FILE, mode='w')
    
    writer = csv.writer(csv_file)
    # Header compatible with existing visualization code
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])
    
    success_count = 0
    benign_count = 0
    sdc_count = 0
    crash_count = 0
    
    print("Starting fault injection campaign...")
    print()
    
    for fault_id in range(TOTAL_FAULTS):
        # Generate random fault parameters (Marvin-style)
        target_reg = random.choice(TARGET_REGISTERS)
        bit_pos = random.randint(0, 63)
        
        # Log fault parameters (Marvin's logging)
        log_file.write(f"{fault_id}: reg: {target_reg} pos: {bit_pos}\n")
        
        # Collect HPC data for multiple runs (Marvin's num_of_run)
        hpc_samples = []
        
        for run in range(NUM_RUNS_PER_FAULT):
            success, hpc_data = inject_fault_gdb(target_reg, bit_pos)
            
            if success and hpc_data:
                hpc_samples.append(hpc_data)
            else:
                break  # Crash occurred
        
        # Classify outcome (Marvin's classification)
        outcome = classify_outcome(hpc_samples, NUM_RUNS_PER_FAULT)
        log_file.write(f"{outcome}\n")
        
        # Write HPC data to CSV (compatible with existing format)
        for hpc_data in hpc_samples:
            # label=1 for faulty data (compatible with existing code)
            writer.writerow(hpc_data + [1])
            success_count += 1
        
        # Update statistics
        if outcome == "benign":
            benign_count += 1
        elif outcome == "SDC":
            sdc_count += 1
        else:  # crash
            crash_count += 1
        
        # Progress log
        if (fault_id + 1) % 100 == 0:
            print(f"Progress: {fault_id + 1}/{TOTAL_FAULTS} faults")
            print(f"  Collected: {success_count} HPC samples")
            print(f"  Benign: {benign_count}, SDC: {sdc_count}, Crash: {crash_count}")
            print()
    
    # Close files
    csv_file.close()
    log_file.close()
    
    # Final summary
    print()
    print("=" * 60)
    print("Collection completed!")
    print("=" * 60)
    print(f"Total faults: {TOTAL_FAULTS}")
    print(f"HPC samples collected: {success_count}")
    print(f"Outcomes:")
    print(f"  - Benign: {benign_count} ({benign_count/TOTAL_FAULTS*100:.1f}%)")
    print(f"  - SDC: {sdc_count} ({sdc_count/TOTAL_FAULTS*100:.1f}%)")
    print(f"  - Crash: {crash_count} ({crash_count/TOTAL_FAULTS*100:.1f}%)")
    print()
    print(f"Data saved to: {OUTPUT_FILE}")
    print(f"Log saved to: {LOG_FILE}")
    print()
    print("You can now visualize with:")
    print(f"  python3 visualize/visualize_marvin.py {BENCHMARK}")
    print("=" * 60)


if __name__ == "__main__":
    main()
