# =========================================
# UNSUPERVISED DATASET IMPROVEMENT PIPELINE
# INPUT : numerical_features_medical_random.csv
# OUTPUT: improved_medical_features.csv
# =========================================

import pandas as pd
import numpy as np

# ---------------------------------
# 1. Load dataset (features only)
# ---------------------------------
df = pd.read_csv("output/numerical_features_medical_random.csv")

# Clean column names
df.columns = df.columns.str.strip()

print("Columns in dataset:", df.columns.tolist())

X = df.copy()

# ---------------------------------
# 2. Handle outliers (1%–99% clipping)
# ---------------------------------
X_out = X.copy()
for col in X_out.columns:
    low = X_out[col].quantile(0.01)
    high = X_out[col].quantile(0.99)
    X_out[col] = X_out[col].clip(low, high)

# ---------------------------------
# 3. Reduce skewness (log transform)
# ---------------------------------
X_log = X_out.copy()
for col in X_log.columns:
    if (X_log[col] > 0).all():
        X_log[col] = np.log1p(X_log[col])

# ---------------------------------
# 4. Feature interaction & ratio creation
# ---------------------------------
X_feat = X_log.copy()
cols = X_feat.columns.tolist()

for i in range(len(cols)):
    for j in range(i + 1, min(i + 4, len(cols))):
        c1, c2 = cols[i], cols[j]
        X_feat[f"{c1}_plus_{c2}"] = X_feat[c1] + X_feat[c2]
        X_feat[f"{c1}_minus_{c2}"] = X_feat[c1] - X_feat[c2]
        X_feat[f"{c1}_ratio_{c2}"] = X_feat[c1] / (X_feat[c2] + 1e-6)

# ---------------------------------
# 5. Save improved dataset
# ---------------------------------
X_feat.to_csv("improved_medical_features.csv", index=False)

print("=================================")
print("✅ FEATURE-ONLY DATASET IMPROVEMENT COMPLETE")
print("Original features:", X.shape[1])
print("Final features:", X_feat.shape[1])
print("Saved file: improved_medical_features.csv")
print("=================================")

