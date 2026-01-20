# Makefile for Raspberry Pi 4 Fault Injector
# Marvin-style implementation

CC = gcc
CFLAGS = -g -O0 -Wall
PYTHON = python3

# Targets
TARGET_APP = target_app
BENCHMARKS = basicmath_bench qsort_bench sha_bench
INJECTORS = simple_injector simple_runner simple_injector_fast simple_runner_fast

.PHONY: all clean setup test run-example help

all: $(TARGET_APP) $(BENCHMARKS) $(INJECTORS)

# Compile target application
$(TARGET_APP): target_app.c
	$(CC) $(CFLAGS) $< -o $@
	@echo "✓ Compiled $(TARGET_APP)"

# Compile benchmarks
basicmath_bench: example_benchmark.c
	$(CC) $(CFLAGS) -DBENCHMARK=1 $< -o $@ -lm
	@echo "✓ Compiled basicmath_bench"

qsort_bench: example_benchmark.c
	$(CC) $(CFLAGS) -DBENCHMARK=2 $< -o $@
	@echo "✓ Compiled qsort_bench"

sha_bench: example_benchmark.c
	$(CC) $(CFLAGS) -DBENCHMARK=3 $< -o $@
	@echo "✓ Compiled sha_bench"

# Compile injectors
simple_injector: simple_injector.c
	$(CC) $(CFLAGS) $< -o $@
	@echo "✓ Compiled simple_injector"

simple_runner: simple_runner.c
	$(CC) $(CFLAGS) $< -o $@
	@echo "✓ Compiled simple_runner"

simple_injector_fast: simple_injector_fast.c
	$(CC) $(CFLAGS) $< -o $@
	@echo "✓ Compiled simple_injector_fast"

simple_runner_fast: simple_runner_fast.c
	$(CC) $(CFLAGS) $< -o $@
	@echo "✓ Compiled simple_runner_fast"

# Setup environment
setup:
	@echo "Setting up Raspberry Pi 4 Fault Injector..."
	@chmod +x setup_rpi_injector.sh
	@./setup_rpi_injector.sh

# Test basic functionality
test: $(TARGET_APP)
	@echo "Testing basic fault injection (10 faults)..."
	$(PYTHON) collect_marvin_style.py target

# Run example campaign
run-example: basicmath_bench
	@echo "Running example fault injection campaign (basicmath)..."
	$(PYTHON) collect_normal.py basicmath
	$(PYTHON) collect_marvin_style.py basicmath

# Run all benchmarks
run-all: $(BENCHMARKS)
	@echo "Running fault injection on all benchmarks..."
	$(PYTHON) collect_normal.py basicmath
	$(PYTHON) collect_marvin_style.py basicmath
	$(PYTHON) collect_normal.py qsort
	$(PYTHON) collect_marvin_style.py qsort
	$(PYTHON) collect_normal.py sha
	$(PYTHON) collect_marvin_style.py sha

# Collect data (Marvin-style, compatible with existing visualization)
collect-normal: basicmath_bench
	@echo "Collecting normal execution data (basicmath)..."
	$(PYTHON) collect_normal.py basicmath

collect-marvin: basicmath_bench
	@echo "Collecting faulty data (Marvin-style, basicmath)..."
	$(PYTHON) collect_marvin_style.py basicmath

collect-all: collect-normal collect-marvin
	@echo "✓ Data collection completed!"
	@echo "  - data/normal_basicmath.csv"
	@echo "  - data/faulty_basicmath_marvin.csv"
	@echo "  - data/fault_log_basicmath_marvin.txt"

# Visualize data
visualize: collect-all
	@echo "Creating visualizations..."
	cd visualize && $(PYTHON) visualize_marvin.py basicmath
	@echo "✓ Visualizations created!"

# Clean build artifacts
clean:
	rm -f $(TARGET_APP) $(BENCHMARKS) $(INJECTORS)
	rm -f *.o *.csv *.log
	rm -f /tmp/gdb_inject.txt /tmp/gdb_inject_marvin.txt
	rm -f visualize/*.png
	@echo "✓ Cleaned build artifacts"

# Help
help:
	@echo "Raspberry Pi 4 Fault Injector - Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all              - Compile all targets and benchmarks"
	@echo "  setup            - Setup environment (install dependencies)"
	@echo "  test             - Run quick test (10 faults)"
	@echo "  run-example      - Run example campaign (basicmath)"
	@echo "  run-all          - Run full campaign on all benchmarks"
	@echo "  collect-normal   - Collect normal execution data (basicmath)"
	@echo "  collect-marvin   - Collect faulty data (Marvin-style, basicmath)"
	@echo "  collect-all      - Collect both normal and faulty data"
	@echo "  visualize        - Collect data and create visualizations"
	@echo "  clean            - Remove build artifacts"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "Quick Start:"
	@echo "  make all           # Compile"
	@echo "  make collect-all   # Collect data (basicmath)"
	@echo "  make visualize     # Visualize"
	@echo ""
	@echo "Manual usage:"
	@echo "  python3 collect_normal.py [benchmark]"
	@echo "  python3 collect_marvin_style.py [benchmark]"
	@echo "  python3 collect_native_fault.py [benchmark]"
	@echo ""
	@echo "Benchmarks: basicmath, qsort, sha, target"
	@echo ""
	@echo "Examples:"
	@echo "  python3 collect_normal.py basicmath"
	@echo "  python3 collect_marvin_style.py qsort"
	@echo "  cd visualize && python3 visualize_marvin.py sha"
