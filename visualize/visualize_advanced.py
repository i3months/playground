import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import os

# 1. Load and merge datasets
# Ensure CSV files from Raspberry Pi are in the same folder
normal_df = pd.read_csv("target_normal_hpc_data.csv")
faulty_df = pd.read_csv("faulty_hpc_data_gdb.csv")
total_df = pd.concat([normal_df, faulty_df], ignore_index=True)

metrics = ["cycles", "instructions", "cache_misses", "branch_misses"]
x = total_df[metrics]
y = total_df['label']

# Z-Normalization is essential to handle different scales
x_scaled = StandardScaler().fit_transform(x)

fig = plt.figure(figsize=(16, 7))

# --- Plot 1: t-SNE (2D) ---
# t-SNE excels at showing local clusters by pushing dissimilar points far apart
print("Running t-SNE... (This might take a few seconds)")
# Fixed: Changed 'n_iter' to 'max_iter' for compatibility with newer sklearn versions
tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=1000)
tsne_results = tsne.fit_transform(x_scaled)

df_tsne = pd.DataFrame(data=tsne_results, columns=['Dim1', 'Dim2'])
df_tsne['label'] = y

ax1 = fig.add_subplot(121)
sns.scatterplot(x='Dim1', y='Dim2', hue='label', data=df_tsne, palette='viridis', s=60, alpha=0.7, ax=ax1)
ax1.set_title("t-SNE: Clear Cluster Separation", fontsize=14)
ax1.grid(True)

# --- Plot 2: PCA (3D) ---
# Visualizing in 3D to see the depth of the data separation
print("Running 3D PCA...")
pca = PCA(n_components=3)
pca_results = pca.fit_transform(x_scaled)

df_pca3d = pd.DataFrame(data=pca_results, columns=['PC1', 'PC2', 'PC3'])
df_pca3d['label'] = y

ax2 = fig.add_subplot(122, projection='3d')
# Plotting Normal and Faulty data points in 3D space
ax2.scatter(df_pca3d.loc[df_pca3d['label']==0, 'PC1'], 
            df_pca3d.loc[df_pca3d['label']==0, 'PC2'], 
            df_pca3d.loc[df_pca3d['label']==0, 'PC3'], 
            c='purple', label='0 (Normal)', s=60, alpha=0.5)
ax2.scatter(df_pca3d.loc[df_pca3d['label']==1, 'PC1'], 
            df_pca3d.loc[df_pca3d['label']==1, 'PC2'], 
            df_pca3d.loc[df_pca3d['label']==1, 'PC3'], 
            c='yellow', label='1 (Faulty)', s=60, alpha=0.5)

ax2.set_title("3D PCA: Spatial Distribution", fontsize=14)
ax2.set_xlabel("PC1")
ax2.set_ylabel("PC2")
ax2.set_zlabel("PC3")
ax2.legend()
ax2.view_init(elev=20, azim=-60)

plt.tight_layout()
plt.savefig("advanced_visualization_fixed.png")
print("Saved: advanced_visualization_fixed.png")