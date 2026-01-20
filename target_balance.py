import pandas as pd
import numpy as np

# ---------------------------------
# 1. Load data
# ---------------------------------
df = pd.read_csv("final_preprocessed_feature_engineered_data.csv")

# ---------------------------------
# 2. Create CONTINUOUS risk score
#    (NO binary thresholds)
# ---------------------------------
df["continuous_risk_score"] = (
    0.25 * df["blood_sugar"] +
    0.20 * df["cholesterol"] +
    0.15 * (50 - df["hemoglobin"]) +   # inverse risk
    0.15 * df["alkaline_phosphatase"] +
    0.25 * df["cancer_severity_score"]
)

# Normalize score
df["continuous_risk_score"] = (
    (df["continuous_risk_score"] - df["continuous_risk_score"].min()) /
    (df["continuous_risk_score"].max() - df["continuous_risk_score"].min())
)

# ---------------------------------
# 3. Quantile-based target (NOW WORKS)
# ---------------------------------
threshold = df["continuous_risk_score"].quantile(0.70)

df["binary_diet"] = (df["continuous_risk_score"] >= threshold).astype(int)

# ---------------------------------
# 4. Verify balance
# ---------------------------------
print("\nClass Distribution:")
print(df["binary_diet"].value_counts())

print("\nClass Percentage:")
print(df["binary_diet"].value_counts(normalize=True) * 100)

# ---------------------------------
# 5. Save dataset
# ---------------------------------
df.to_csv("final_preprocessed_with_target.csv", index=False)

print("\n✅ FINAL usable target created successfully")



