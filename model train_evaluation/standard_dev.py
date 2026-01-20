import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import StratifiedKFold, cross_val_score
from lightgbm import LGBMClassifier

warnings.filterwarnings("ignore")

df = pd.read_csv("separate features/final_preprocessed_with_target.csv")

target_column = "binary_diet"

leakage_columns = [
    "blood_sugar",
    "cholesterol",
    "hemoglobin",
    "alkaline_phosphatase",
    "cancer_severity_score",
    "diet_risk_score",
    "continuous_risk_score",
    "liver_risk_score"
]

X = df.drop(columns=leakage_columns + [target_column], errors="ignore")
y = df[target_column]

model = LGBMClassifier(
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=31,
    random_state=42,
    verbose=-1
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

f1_scores = cross_val_score(
    model,
    X,
    y,
    cv=cv,
    scoring="f1"
)

print("📊 LightGBM Cross-Validation Evaluation")
print(f"Mean F1-Score       : {np.mean(f1_scores)*100:.2f}%")
print(f"Standard Deviation  : {np.std(f1_scores)*100:.2f}%")

