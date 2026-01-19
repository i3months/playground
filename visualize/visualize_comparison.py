import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
data_files = {
    "Normal (ptrace)": "data/ptrace_normal_basicmath.csv",
    "Fault (ptrace)": "data/faulty_basicmath_native.csv"
}

# 모든 데이터 로드
all_data = []
for name, filepath in data_files.items():
    if Path(filepath).exists():
        df = pd.read_csv(filepath)
        df['method'] = name
        all_data.append(df)
        print(f"✓ {name}: {len(df)} samples")
    else:
        print(f"✗ {filepath} not found")

if len(all_data) == 0:
    print("\n❌ No data files found!")
    print("Please run:")
    print("  python3 collect_ptrace_normal.py basicmath")
    print("  python3 collect_native_fault.py basicmath")
    exit(1)

combined_df = pd.concat(all_data, ignore_index=True)
print(f"\nTotal: {len(combined_df)} samples")

# 시각화
fig = plt.figure(figsize=(18, 10))

metrics = ['cycles', 'instructions', 'cache_misses', 'branch_misses']

# 1. Boxplot 비교
for idx, metric in enumerate(metrics, 1):
    ax = plt.subplot(3, 4, idx)
    sns.boxplot(data=combined_df, x='method', y=metric, hue='method', palette='Set2', legend=False)
    ax.set_title(f'{metric.replace("_", " ").title()}', fontsize=12, fontweight='bold')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=15)
    ax.grid(True, alpha=0.3)

# 2. Histogram 분포
for idx, metric in enumerate(metrics, 1):
    ax = plt.subplot(3, 4, idx + 4)
    for method in data_files.keys():
        if method in combined_df['method'].values:
            data = combined_df[combined_df['method'] == method][metric]
            ax.hist(data, bins=50, alpha=0.6, label=method)
    ax.set_title(f'{metric.replace("_", " ").title()} Distribution', fontsize=12)
    ax.set_xlabel(metric)
    ax.set_ylabel('Frequency')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

# 3. 통계 요약
ax = plt.subplot(3, 2, 5)
stats_data = []
for method in data_files.keys():
    if method in combined_df['method'].values:
        method_df = combined_df[combined_df['method'] == method]
        stats_data.append([
            method,
            len(method_df),
            f"{method_df['cycles'].mean():.0f}",
            f"{method_df['instructions'].mean():.0f}",
            f"{method_df['cache_misses'].mean():.0f}",
            f"{method_df['branch_misses'].mean():.0f}"
        ])

ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=stats_data,
                colLabels=['Method', 'Count', 'Cycles', 'Instructions', 'Cache Miss', 'Branch Miss'],
                cellLoc='center',
                loc='center',
                colWidths=[0.25, 0.1, 0.15, 0.15, 0.15, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)
ax.set_title('Statistics Summary', fontsize=12, fontweight='bold', pad=20)

# 4. PCA 2D 시각화
ax = plt.subplot(3, 2, 6)
X = combined_df[metrics].values
y = combined_df['method'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

colors = {'Normal (ptrace)': 'blue', 'Fault (ptrace)': 'red'}
for method in data_files.keys():
    if method in combined_df['method'].values:
        mask = y == method
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1], 
                  label=method, alpha=0.5, s=30, c=colors.get(method, 'gray'))

ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
ax.set_title('PCA: Normal vs Fault Separation', fontsize=12, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)

plt.suptitle('Fault Injection: Normal vs Fault (Ptrace Method)', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('visualize/normal_vs_fault_comparison.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: visualize/normal_vs_fault_comparison.png")
plt.show()
