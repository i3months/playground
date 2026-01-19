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
OUTPUT_FILE = f"data/faulty_{BENCHMARK}_native.csv"
INJECTOR = "./simple_injector"

# Check if binaries exist
if not os.path.exists(INJECTOR) or not os.path.exists(TARGET_APP):
    print(f"Error: '{INJECTOR}' or '{TARGET_APP}' not found.")
    print("Please compile: make all")
    sys.exit(1)

os.makedirs("data", exist_ok=True)

print("=" * 60)
print("Native Fault Injection (ptrace)")
print("=" * 60)
print(f"Benchmark: {BENCHMARK}")
print(f"Target: {TARGET_APP}")
print(f"Total runs: {TOTAL_RUNS}")
print(f"Output: {OUTPUT_FILE}")
print("=" * 60)
print()

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
                writer.writerow(data_row + ["3"])  # label=3: ptrace native
                success_count += 1
            
        except subprocess.CalledProcessError:
            # Fault injection can sometimes crash the process violently
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