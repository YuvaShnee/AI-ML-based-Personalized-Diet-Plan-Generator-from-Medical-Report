
import pandas as pd

# 1️⃣ Load the train and test CSVs
train_df = pd.read_csv("split/train_data.csv")
test_df  = pd.read_csv("split/test_data.csv")

target_column = "binary_diet"

# 2️⃣ Columns used to generate the target (leakage)
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

# 3️⃣ Drop leakage columns + target from features
X_train = train_df.drop(columns=leakage_columns + [target_column], errors="ignore")
y_train = train_df[target_column]

X_test = test_df.drop(columns=leakage_columns + [target_column], errors="ignore")
y_test = test_df[target_column]

print("X_train shape:", X_train.shape)
print("X_test shape :", X_test.shape)
print("y_train distribution:\n", y_train.value_counts())
print("y_test distribution:\n", y_test.value_counts())


