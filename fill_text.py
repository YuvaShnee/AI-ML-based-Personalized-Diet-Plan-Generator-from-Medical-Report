import pandas as pd
import numpy as np
import random

# ---------------------------------
# 1. Load dataset
# ---------------------------------
df = pd.read_csv("separate features/all_text_features.csv")
print("Initial shape:", df.shape)

# ---------------------------------
# 2. Replace empty strings with NaN
# ---------------------------------
df = df.replace(r'^\s*$', np.nan, regex=True)

# ---------------------------------
# 3. Drop fully empty rows ONLY
# ---------------------------------
df = df.dropna(how="all").reset_index(drop=True)

# ---------------------------------
# 4. Random realistic patient names
# ---------------------------------
patient_names = [
    "Swetha", "Mala", "Kamala", "Anitha", "Lakshmi", "Revathi",
    "Suresh", "Ramesh", "Karthik", "Arun", "Vijay", "Prakash",
    "Meena", "Geetha", "Kavitha", "Radha", "Priya", "Divya"
]

if "patient name" in df.columns:
    df.loc[df["patient name"].isna(), "patient name"] = [
        random.choice(patient_names)
        for _ in range(df["patient name"].isna().sum())
    ]

# ---------------------------------
# 5. Fill File column correctly (FIXED)
# ---------------------------------
if "file" in df.columns:
    missing_files = df["file"].isna()
    df.loc[missing_files, "file"] = [
        f"Medical_Report_{i+1}.txt"
        for i in df.index[missing_files]
    ]

# ---------------------------------
# 6. Medical text filling for other columns
# ---------------------------------
medical_fill_map = {
    "gender": ["Male", "Female"],
    "diagnosis": "Clinical findings suggest a non-malignant condition requiring follow-up",
    "prescription": "Supportive medical management advised with routine follow-up",
    "specimen": "Biopsy tissue specimen received for pathological examination",
    "material": "Formalin-fixed tissue sample",
    "clinical notes": "Patient evaluated clinically; further investigations advised as needed",
    "histopathology diagnosis": "No evidence of malignancy observed in the examined tissue",
    "microscopic description": (
        "Microscopic examination shows preserved tissue architecture "
        "without atypical cellular features"
    )
}

for col in df.columns:
    col_lower = col.lower()

    if col_lower == "gender":
        missing = df[col].isna()
        df.loc[missing, col] = [
            random.choice(medical_fill_map["gender"])
            for _ in range(missing.sum())
        ]

    elif col_lower in medical_fill_map:
        df[col] = df[col].fillna(medical_fill_map[col_lower])

# ---------------------------------
# 7. Final validation
# ---------------------------------
print("Remaining empty cells:", df.isna().sum().sum())
print("Final shape:", df.shape)

# ---------------------------------
# 8. Save final dataset
# ---------------------------------
df.to_csv("all_text_features_medical_filled.csv", index=False)

print("✅ Medical text filled successfully")

