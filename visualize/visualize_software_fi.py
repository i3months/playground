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
normal = pd.read_csv('data/software_normal_basicmath.csv')
fault = pd.read_csv('data/software_fault_basicmath.csv')

print(f"✓ Normal: {len(normal)} samples")
print(f"✓ Fault: {len(fault)} samples")

# Outlier 제거 (IQR 방법)
def remove_outliers(df, column, factor=3):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - factor * IQR
    upper = Q3 + factor * IQR
    return df[(df[column] >= lower) & (df[column] <= upper)]

# Fault 데이터에서 extreme outlier 제거
fault_clean = remove_outliers(fault, 'cycles', factor=3)
fault_clean = remove_outliers(fault_clean, 'instructions', factor=3)

print(f"✓ Fault (cleaned): {len(fault_clean)} samples (removed {len(fault) - len(fault_clean)} outliers)")

# 데이터 합치기
normal['method'] = 'Normal'
fault_clean['method'] = 'Fault'
combined_df = pd.concat([normal, fault_clean], ignore_index=True)

# 시각화
fig = plt.figure(figsize=(18, 10))
metrics = ['cycles', 'instructions', 'cache_misses', 'branch_misses']

# 1. Boxplot
for idx, metric in enumerate(metrics, 1):
    ax = plt.subplot(3, 4, idx)
    sns.boxplot(data=combined_df, x='method', y=metric, hue='method', palette='Set2', legend=False)
    ax.set_title(f'{metric.replace("_", " ").title()}', fontsize=12, fontweight='bold')
    ax.set_xlabel('')
    ax.grid(True, alpha=0.3)

# 2. Histogram
for idx, metric in enumerate(metrics, 1):
    ax = plt.subplot(3, 4, idx + 4)
    for method in ['Normal', 'Fault']:
        data = combined_df[combined_df['method'] == method][metric]
        ax.hist(data, bins=50, alpha=0.6, label=method)
    ax.set_title(f'{metric.replace("_", " ").title()} Distribution', fontsize=12)
    ax.set_xlabel(metric)
    ax.set_ylabel('Frequency')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

# 3. 통계 테이블
ax = plt.subplot(3, 2, 5)
stats_data = []
for method in ['Normal', 'Fault']:
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
                colWidths=[0.2, 0.1, 0.15, 0.15, 0.15, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)
ax.set_title('Statistics Summary (Outliers Removed)', fontsize=12, fontweight='bold', pad=20)

# 4. PCA
ax = plt.subplot(3, 2, 6)
X = combined_df[metrics].values
y = combined_df['method'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

colors = {'Normal': 'blue', 'Fault': 'red'}
for method in ['Normal', 'Fault']:
    mask = y == method
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1], 
              label=method, alpha=0.5, s=30, c=colors[method])

ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
ax.set_title('PCA: Normal vs Fault Separation', fontsize=12, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)

plt.suptitle('Software-based Fault Injection: Normal vs Fault', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('visualize/software_fi_final.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: visualize/software_fi_final.png")
plt.show()
