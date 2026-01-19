import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os

# 1. Configuration: File paths and metrics
NORMAL_FILE = "target_normal_hpc_data.csv"
FAULTY_FILE = "faulty_hpc_data_gdb.csv"
METRICS = ["cycles", "instructions", "cache_misses", "branch_misses"]

# 2. Load and merge datasets
if not os.path.exists(NORMAL_FILE) or not os.path.exists(FAULTY_FILE):
    print("Error: CSV files not found. Ensure both files are in the same directory.")
    exit(1)

df_normal = pd.read_csv(NORMAL_FILE)
df_faulty = pd.read_csv(FAULTY_FILE)
df_total = pd.concat([df_normal, df_faulty], ignore_index=True)

# 3. Create Boxplots with Log Scale
# Since faulty data is orders of magnitude larger, log scale is used for better comparison.
plt.figure(figsize=(14, 10))
for i, metric in enumerate(METRICS, 1):
    plt.subplot(2, 2, i)
    sns.boxplot(x='label', y=metric, data=df_total, palette="Set2")
    plt.yscale('log')  # Apply log scale due to massive scale difference
    plt.title(f"HPC Metric Distribution: {metric}")
    plt.xlabel("Label (0: Normal, 1: Faulty)")
    plt.ylabel(f"{metric} (log scale)")

plt.tight_layout()
plt.savefig("hpc_boxplot_comparison.png")
print("Saved: hpc_boxplot_comparison.png")

# 4. Principal Component Analysis (PCA)
# PCA reduces 4-dimensional HPC data into 2D to visualize class separation.
x = df_total[METRICS]
y = df_total['label']

# Standardize features (Z-normalization) before PCA
x_scaled = StandardScaler().fit_transform(x)

pca = PCA(n_components=2)
pc_results = pca.fit_transform(x_scaled)
df_pca = pd.DataFrame(data=pc_results, columns=['PC1', 'PC2'])
df_pca['label'] = y

plt.figure(figsize=(10, 7))
sns.scatterplot(x='PC1', y='PC2', hue='label', data=df_pca, palette="viridis", alpha=0.6)
plt.title("HPC Data Clustering via PCA (Normal vs. Faulty)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.grid(True)

plt.savefig("hpc_pca_clustering.png")
print("Saved: hpc_pca_clustering.png")