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
# 4. Patient names (random)
# ---------------------------------
patient_names = [
    "Swetha", "Mala", "Kamala", "Anitha", "Lakshmi", "Revathi",
    "Suresh", "Ramesh", "Karthik", "Arun", "Vijay", "Prakash",
    "Meena", "Geetha", "Kavitha", "Radha", "Priya", "Divya"
]

if "patient_name" in df.columns:
    missing = df["patient_name"].isna()
    df.loc[missing, "patient_name"] = random.choices(patient_names, k=missing.sum())

# ---------------------------------
# 5. File column
# ---------------------------------
if "file" in df.columns:
    missing = df["file"].isna()
    df.loc[missing, "file"] = [
        f"Medical_Report_{i+1}.txt" for i in df.index[missing]
    ]

# ---------------------------------
# 6. Gender
# ---------------------------------
if "gender" in df.columns:
    missing = df["gender"].isna()
    df.loc[missing, "gender"] = random.choices(["Male", "Female"], k=missing.sum())

# ---------------------------------
# 7. Specimen (random medical text)
# ---------------------------------
specimen_texts = [
    "Core needle biopsy tissue",
    "Excisional biopsy specimen",
    "Fine needle aspiration sample",
    "Surgical resection specimen",
    "Endoscopic biopsy material",
    "Incisional biopsy tissue"
]

if "specimen" in df.columns:
    missing = df["specimen"].isna()
    df.loc[missing, "specimen"] = random.choices(specimen_texts, k=missing.sum())

# ---------------------------------
# 8. Medical text columns (FIXED)
# ---------------------------------
medical_fill = {
    "clinical_notes": [
        "Patient evaluated clinically with relevant symptoms; further assessment advised",
        "Clinical examination performed; findings correlated with investigations",
        "Patient reviewed and clinical history documented"
    ],
    "histopathology_diagnosis": [
        "Histopathological examination reveals benign tissue changes",
        "No evidence of malignancy identified on histopathological analysis",
        "Findings consistent with non-neoplastic pathology"
    ],
    "microscopic_description": [
        "Microscopic examination shows preserved tissue architecture without dysplasia",
        "Sections reveal normal cellular morphology with no atypical features",
        "Tissue sections demonstrate mild inflammatory changes without malignancy"
    ],
    "diagnosis": [
        "Findings suggest a benign pathological condition",
        "Clinical and pathological findings are non-malignant",
        "Diagnosis consistent with a non-neoplastic condition"
    ],
    "prescription": [
        "Supportive medical management advised with follow-up",
        "Symptomatic treatment recommended as per clinical guidelines",
        "Medical management initiated; review on follow-up"
    ],
    "material": [
        "Formalin-fixed paraffin-embedded tissue",
        "Preserved biological tissue material",
        "Processed tissue specimen for microscopic examination"
    ]
}

for col, texts in medical_fill.items():
    if col in df.columns:
        missing = df[col].isna()
        df.loc[missing, col] = random.choices(texts, k=missing.sum())

# ---------------------------------
# 9. Final validation
# ---------------------------------
print("Remaining empty cells:", df.isna().sum().sum())
print("Final shape:", df.shape)

# ---------------------------------
# 10. Save cleaned dataset
# ---------------------------------
df.to_csv("text_features_medical_filled.csv", index=False)

print("✅ All medical text filled correctly")
