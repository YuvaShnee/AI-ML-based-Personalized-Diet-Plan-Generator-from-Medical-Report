import pandas as pd
import numpy as np

# Load file
df = pd.read_csv("separate features/all_text_features.csv")

print("Initial shape:", df.shape)

# ---------------------------------
# 1. Convert empty strings / spaces to NaN
# ---------------------------------
df = df.replace(r'^\s*$', np.nan, regex=True)

# ---------------------------------
# 2. Count empty rows (all columns NaN)
# ---------------------------------
empty_rows = df.isna().all(axis=1).sum()
print("Empty rows (fully blank):", empty_rows)

# ---------------------------------
# 3. Drop fully empty rows ONLY
# ---------------------------------
df_cleaned = df.dropna(how="all")

# ---------------------------------
# 4. Remove duplicate rows
# ---------------------------------
df_cleaned = df_cleaned.drop_duplicates()

# ---------------------------------
# 5. Reset index
# ---------------------------------
df_cleaned.reset_index(drop=True, inplace=True)

# ---------------------------------
# 6. Save cleaned file
# ---------------------------------
df_cleaned.to_csv("all_text_features_cleaned.csv", index=False)

print("Cleaned shape:", df_cleaned.shape)
print("✅ Data cleaning completed")


