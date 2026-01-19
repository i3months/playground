#!/usr/bin/env python3
"""
Visualization for Marvin-style collected data
Compatible with both old and new data formats
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
import sys

# 벤치마크 선택 (명령줄 인자 또는 기본값)
if len(sys.argv) > 1:
    BENCHMARK = sys.argv[1]
else:
    BENCHMARK = "basicmath"  # 기본값

# Configuration
NORMAL_FILE = f"../data/normal_{BENCHMARK}.csv"
FAULTY_FILE = f"../data/faulty_{BENCHMARK}_marvin.csv"
METRICS = ["cycles", "instructions", "cache_misses", "branch_misses"]

# Check if files exist
if not os.path.exists(NORMAL_FILE):
    print(f"Error: {NORMAL_FILE} not found.")
    print(f"Please run: python3 collect_normal.py {BENCHMARK}")
    sys.exit(1)

if not os.path.exists(FAULTY_FILE):
    print(f"Error: {FAULTY_FILE} not found.")
    print(f"Please run: python3 collect_marvin_style.py {BENCHMARK}")
    sys.exit(1)

# Load datasets
print("=" * 60)
print(f"Visualizing: {BENCHMARK}")
print("=" * 60)
print("Loading datasets...")
df_normal = pd.read_csv(NORMAL_FILE)
df_faulty = pd.read_csv(FAULTY_FILE)

print(f"Normal samples: {len(df_normal)}")
print(f"Faulty samples: {len(df_faulty)}")

# Merge datasets
df_total = pd.concat([df_normal, df_faulty], ignore_index=True)
print(f"Total samples: {len(df_total)}")
print()

# ============================================
# Plot 1: Boxplots with Log Scale
# ============================================
print("Creating boxplot comparison...")
plt.figure(figsize=(14, 10))

for i, metric in enumerate(METRICS, 1):
    plt.subplot(2, 2, i)
    sns.boxplot(x='label', y=metric, data=df_total, palette="Set2")
    plt.yscale('log')
    plt.title(f"HPC Metric Distribution: {metric}")
    plt.xlabel("Label (0: Normal, 1: Faulty)")
    plt.ylabel(f"{metric} (log scale)")

plt.tight_layout()
output_file = f"hpc_boxplot_{BENCHMARK}.png"
plt.savefig(output_file)
print(f"✓ Saved: {output_file}")
plt.close()

# ============================================
# Plot 2: PCA Clustering
# ============================================
print("Creating PCA clustering...")
x = df_total[METRICS]
y = df_total['label']

# Standardize features
x_scaled = StandardScaler().fit_transform(x)

# PCA
pca = PCA(n_components=2)
pc_results = pca.fit_transform(x_scaled)
df_pca = pd.DataFrame(data=pc_results, columns=['PC1', 'PC2'])
df_pca['label'] = y

plt.figure(figsize=(10, 7))
sns.scatterplot(x='PC1', y='PC2', hue='label', data=df_pca, palette="viridis", alpha=0.6)
plt.title(f"HPC Data Clustering via PCA ({BENCHMARK})")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.grid(True)

output_file = f"hpc_pca_{BENCHMARK}.png"
plt.savefig(output_file)
print(f"✓ Saved: {output_file}")
plt.close()

# ============================================
# Plot 3: Statistical Summary
# ============================================
print("Creating statistical summary...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for i, metric in enumerate(METRICS):
    ax = axes[i // 2, i % 2]
    
    normal_data = df_normal[metric]
    faulty_data = df_faulty[metric]
    
    ax.hist(normal_data, bins=50, alpha=0.5, label='Normal', color='blue')
    ax.hist(faulty_data, bins=50, alpha=0.5, label='Faulty', color='red')
    
    ax.set_xlabel(metric)
    ax.set_ylabel('Frequency')
    ax.set_title(f'{metric} Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
output_file = f"hpc_histogram_{BENCHMARK}.png"
plt.savefig(output_file)
print(f"✓ Saved: {output_file}")
plt.close()

# ============================================
# Statistics Summary
# ============================================
print()
print("=" * 60)
print("Statistical Summary")
print("=" * 60)

for metric in METRICS:
    normal_mean = df_normal[metric].mean()
    faulty_mean = df_faulty[metric].mean()
    normal_std = df_normal[metric].std()
    faulty_std = df_faulty[metric].std()
    
    print(f"\n{metric}:")
    print(f"  Normal: {normal_mean:,.0f} ± {normal_std:,.0f}")
    print(f"  Faulty: {faulty_mean:,.0f} ± {faulty_std:,.0f}")
    print(f"  Difference: {abs(faulty_mean - normal_mean):,.0f} ({abs(faulty_mean - normal_mean) / normal_mean * 100:.1f}%)")

print()
print("=" * 60)
print("Visualization completed!")
print("=" * 60)
print("Generated files:")
print(f"  - hpc_boxplot_{BENCHMARK}.png")
print(f"  - hpc_pca_{BENCHMARK}.png")
print(f"  - hpc_histogram_{BENCHMARK}.png")
print("=" * 60)
