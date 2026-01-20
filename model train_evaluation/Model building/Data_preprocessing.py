import pandas as pd
import numpy as np
import os

# ----------------------------------
# PATHS
# ----------------------------------
input_file = "output/numerical_features_medical_random.csv"
output_file = "output/preprocessed/data_preprocessed.csv"

os.makedirs("output/preprocessed", exist_ok=True)

# ----------------------------------
# LOAD DATA
# ----------------------------------
df = pd.read_csv(input_file)
print("✔ Dataset loaded:", df.shape)

# ----------------------------------
# NUMERIC SAFETY
# ----------------------------------
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col].fillna(df[col].median(), inplace=True)

print("✔ Numeric conversion & NaN handling done")

# ----------------------------------
# OUTLIER CLIPPING (MEDICAL SAFE)
# ----------------------------------
for col in df.columns:
    if col != "age":
        low = df[col].quantile(0.01)
        high = df[col].quantile(0.99)
        df[col] = df[col].clip(low, high)

print("✔ Outliers clipped")

# ----------------------------------
# SAVE
# ----------------------------------
df.to_csv(output_file, index=False)
print("🎉 Preprocessed data saved:", output_file)
