#!/bin/bash
# Raspberry Pi 4 Fault Injector Setup Script
# Marvin-style implementation setup

echo "=========================================="
echo "Raspberry Pi 4 Fault Injector Setup"
echo "Marvin-style Implementation"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi 4"
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update -qq

# Install required packages
echo "[2/6] Installing required packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    gdb \
    linux-tools-generic \
    linux-tools-common \
    build-essential \
    git

# Install Python packages
echo "[3/6] Installing Python packages..."
pip3 install pandas matplotlib seaborn scikit-learn --user

# Configure perf permissions
echo "[4/6] Configuring perf permissions..."
sudo sysctl -w kernel.perf_event_paranoid=-1
sudo sysctl -w kernel.kptr_restrict=0

# Make permanent
if ! grep -q "kernel.perf_event_paranoid" /etc/sysctl.conf; then
    echo "kernel.perf_event_paranoid = -1" | sudo tee -a /etc/sysctl.conf
fi

if ! grep -q "kernel.kptr_restrict" /etc/sysctl.conf; then
    echo "kernel.kptr_restrict = 0" | sudo tee -a /etc/sysctl.conf
fi

# Compile target application and benchmarks
echo "[5/6] Compiling applications..."
if [ -f "target_app.c" ]; then
    gcc -g -O0 target_app.c -o target_app
    echo "  ✓ target_app compiled"
fi

if [ -f "example_benchmark.c" ]; then
    gcc -g -O0 -DBENCHMARK=1 example_benchmark.c -o basicmath_bench -lm
    gcc -g -O0 -DBENCHMARK=2 example_benchmark.c -o qsort_bench
    gcc -g -O0 -DBENCHMARK=3 example_benchmark.c -o sha_bench
    echo "  ✓ benchmarks compiled"
fi

if [ -f "simple_injector.c" ]; then
    gcc -g -O0 simple_injector.c -o simple_injector
    echo "  ✓ simple_injector compiled"
fi

# Make scripts executable
echo "[6/6] Setting up scripts..."
chmod +x collect_normal.py
chmod +x collect_marvin_style.py
chmod +x collect_native_fault.py
chmod +x visualize/visualize_marvin.py

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  1. Compile: make all"
echo "  2. Collect data: make collect-all"
echo "  3. Visualize: make visualize"
echo ""
echo "Manual usage:"
echo "  python3 collect_normal.py basicmath"
echo "  python3 collect_marvin_style.py basicmath"
echo "  cd visualize && python3 visualize_marvin.py basicmath"
echo ""
echo "For more information, see README.md"
echo ""
