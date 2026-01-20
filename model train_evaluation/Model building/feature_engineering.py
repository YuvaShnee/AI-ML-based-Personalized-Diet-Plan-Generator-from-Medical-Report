import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# ---------------------------------
# 1. Load cleaned dataset
# ---------------------------------
df = pd.read_csv("final_unique_range_valid_medical_data.csv")

print("Initial shape:", df.shape)
print("Columns:", df.columns.tolist())

# ---------------------------------
# 2. Feature Engineering (Medical)
# ---------------------------------

# BMI category (WHO standard)
df["bmi_category"] = pd.cut(
    df["bmi"],
    bins=[0, 18.5, 24.9, 29.9, 100],
    labels=[0, 1, 2, 3]   # underweight, normal, overweight, obese
)

# Anemia indicator
df["anemia_flag"] = (df["hemoglobin"] < 12).astype(int)

# High cholesterol indicator
df["high_cholesterol_flag"] = (df["cholesterol"] > 200).astype(int)

# High blood sugar indicator
df["high_blood_sugar_flag"] = (df["blood_sugar"] > 140).astype(int)

# Liver risk score (only using alkaline phosphatase)
df["liver_risk_score"] = (df["alkaline_phosphatase"] > 120).astype(int)

# Cancer severity score
df["cancer_severity_score"] = (
    df["tumor_size"] +
    df["tumor_grade"] +
    df["stage"] +
    (df["lymph_nodes"] / 5)
)

# ---------------------------------
# 3. Log Transform (Skewed features)
# ---------------------------------
skewed_cols = [
    "cholesterol",
    "blood_sugar",
    "platelet_count",
    "wbc_count",
    "alkaline_phosphatase"
]

for col in skewed_cols:
    if col in df.columns:
        df[col + "_log"] = np.log1p(df[col])

# ---------------------------------
# 4. Drop original skewed columns (optional)
# ---------------------------------
# Uncomment if required
# df.drop(columns=skewed_cols, inplace=True)

# ---------------------------------
# 5. Scaling
# ---------------------------------
scale_cols = [
    "age", "bmi", "cholesterol", "blood_sugar",
    "hemoglobin", "rbc_count", "platelet_count",
    "wbc_count", "alkaline_phosphatase", "total_protein",
    "glucose", "tumor_size"
]

# Keep only columns that exist in dataset
scale_cols = [col for col in scale_cols if col in df.columns]

scaler = StandardScaler()
df[scale_cols] = scaler.fit_transform(df[scale_cols])

# ---------------------------------
# 6. Final dataset ready for ML
# ---------------------------------
df.to_csv("final_preprocessed_feature_engineered_data.csv", index=False)

print("✅ Preprocessing & Feature Engineering completed")
print("Final shape:", df.shape)

