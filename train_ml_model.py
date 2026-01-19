import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 60)
print("Fault Injection Detection - ML Training")
print("=" * 60)

# 데이터 로드
normal_df = pd.read_csv('data/ptrace_normal_basicmath.csv')
fault_df = pd.read_csv('data/faulty_basicmath_native.csv')

print(f"\n✓ Normal samples: {len(normal_df)}")
print(f"✓ Fault samples: {len(fault_df)}")

# 데이터 합치기
df = pd.concat([normal_df, fault_df], ignore_index=True)

# Features와 Labels
X = df[['cycles', 'instructions', 'cache_misses', 'branch_misses']].values
y = df['label'].values

# Train/Test 분리
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# 정규화
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 모델 1: Random Forest
print("\n" + "=" * 60)
print("Training Random Forest...")
print("=" * 60)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
rf_model.fit(X_train_scaled, y_train)

rf_pred = rf_model.predict(X_test_scaled)
rf_acc = accuracy_score(y_test, rf_pred)

print(f"\n✓ Random Forest Accuracy: {rf_acc:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, rf_pred, target_names=['Normal', 'Fault']))

# 모델 2: SVM
print("\n" + "=" * 60)
print("Training SVM...")
print("=" * 60)

svm_model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
svm_model.fit(X_train_scaled, y_train)

svm_pred = svm_model.predict(X_test_scaled)
svm_acc = accuracy_score(y_test, svm_pred)

print(f"\n✓ SVM Accuracy: {svm_acc:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, svm_pred, target_names=['Normal', 'Fault']))

# Feature Importance (Random Forest)
feature_names = ['Cycles', 'Instructions', 'Cache Misses', 'Branch Misses']
importances = rf_model.feature_importances_

print("\n" + "=" * 60)
print("Feature Importance (Random Forest)")
print("=" * 60)
for name, imp in zip(feature_names, importances):
    print(f"{name:20s}: {imp:.4f}")

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Confusion Matrix - Random Forest
cm_rf = confusion_matrix(y_test, rf_pred)
sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues', ax=axes[0, 0],
            xticklabels=['Normal', 'Fault'], yticklabels=['Normal', 'Fault'])
axes[0, 0].set_title(f'Random Forest\nAccuracy: {rf_acc:.2%}')
axes[0, 0].set_ylabel('True Label')
axes[0, 0].set_xlabel('Predicted Label')

# 2. Confusion Matrix - SVM
cm_svm = confusion_matrix(y_test, svm_pred)
sns.heatmap(cm_svm, annot=True, fmt='d', cmap='Greens', ax=axes[0, 1],
            xticklabels=['Normal', 'Fault'], yticklabels=['Normal', 'Fault'])
axes[0, 1].set_title(f'SVM\nAccuracy: {svm_acc:.2%}')
axes[0, 1].set_ylabel('True Label')
axes[0, 1].set_xlabel('Predicted Label')

# 3. Feature Importance
axes[1, 0].barh(feature_names, importances, color='skyblue')
axes[1, 0].set_xlabel('Importance')
axes[1, 0].set_title('Feature Importance (Random Forest)')
axes[1, 0].grid(True, alpha=0.3)

# 4. Model Comparison
models = ['Random Forest', 'SVM']
accuracies = [rf_acc, svm_acc]
axes[1, 1].bar(models, accuracies, color=['blue', 'green'], alpha=0.7)
axes[1, 1].set_ylabel('Accuracy')
axes[1, 1].set_title('Model Comparison')
axes[1, 1].set_ylim([0, 1])
axes[1, 1].grid(True, alpha=0.3, axis='y')
for i, acc in enumerate(accuracies):
    axes[1, 1].text(i, acc + 0.02, f'{acc:.2%}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('visualize/ml_training_results.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: visualize/ml_training_results.png")

print("\n" + "=" * 60)
print("Training completed!")
print("=" * 60)
print(f"\nBest Model: {'Random Forest' if rf_acc > svm_acc else 'SVM'}")
print(f"Best Accuracy: {max(rf_acc, svm_acc):.2%}")
