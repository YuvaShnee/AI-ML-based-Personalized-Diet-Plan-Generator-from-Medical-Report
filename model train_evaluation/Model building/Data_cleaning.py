import pandas as pd
import numpy as np

# 1. Load the dataset
file_path = "output/numerical_features.csv"   # change path if needed
df = pd.read_csv(file_path)

print("Initial Shape:", df.shape)
print("\nColumn Data Types:\n", df.dtypes)

# -----------------------------
# 2. Check for NaN values
# -----------------------------
print("\nMissing Values Count:\n")
print(df.isna().sum())

# Percentage of missing values
print("\nMissing Values Percentage:\n")
print((df.isna().sum() / len(df)) * 100)

# -----------------------------
# 3. Handle NaN values
# -----------------------------
# Fill numerical NaNs with median
num_cols = df.select_dtypes(include=np.number).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Fill categorical NaNs with mode
cat_cols = df.select_dtypes(exclude=np.number).columns
for col in cat_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)

print("\nNaN values after cleaning:\n")
print(df.isna().sum())

# -----------------------------
# 4. Detect Outliers (IQR Method)
# -----------------------------
outlier_summary = {}

for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    outlier_summary[col] = len(outliers)

print("\nOutlier Count per Column:\n")
for k, v in outlier_summary.items():
    print(f"{k}: {v}")

# -----------------------------
# 5. Handle Outliers (Capping)
# -----------------------------
for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
    df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])

print("\nOutliers handled using capping")

# -----------------------------
# 6. Save Cleaned Data
# -----------------------------
cleaned_file = "numerical_features_cleaned.csv"
df.to_csv(cleaned_file, index=False)

print("\nFinal Shape:", df.shape)
print(f"Cleaned file saved as: {cleaned_file}")
