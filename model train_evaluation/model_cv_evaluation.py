import pandas as pd
import joblib
import warnings

from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

warnings.filterwarnings("ignore")

print("\n🚀 RUNNING CROSS-VALIDATED TRAINING SCRIPT 🚀")

# =====================================================
# 1. LOAD DATA
# =====================================================
train_df = pd.read_csv("split/train_data.csv")
test_df  = pd.read_csv("split/test_data.csv")

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

X_train = train_df.drop(columns=leakage_columns + [target_column], errors="ignore")
y_train = train_df[target_column]

X_test = test_df.drop(columns=leakage_columns + [target_column], errors="ignore")
y_test = test_df[target_column]

# =====================================================
# 2. MODELS
# =====================================================
models = {
    "RandomForest": RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=20,
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost": XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.7,
        colsample_bytree=0.7,
        eval_metric="logloss",
        random_state=42
    ),

    "LightGBM": LGBMClassifier(
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=15,
        max_depth=6,
        min_data_in_leaf=30,
        random_state=42
    )
}

# =====================================================
# 3. CROSS-VALIDATION
# =====================================================
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

best_model = None
best_model_name = None
best_test_f1 = 0

print("\nMODEL EVALUATION RESULTS")
print("=" * 70)

# =====================================================
# 4. TRAIN & EVALUATE
# =====================================================
for name, model in models.items():
    print(f"\n🔹 Training {name}...")

    # ---------- TRAIN METRICS (CV) ----------
    y_train_cv_pred = cross_val_predict(
        model,
        X_train,
        y_train,
        cv=cv
    )

    print(f"{name} - TRAIN METRICS (5-FOLD CROSS-VALIDATION)")
    print(f"Accuracy  : {accuracy_score(y_train, y_train_cv_pred)*100:.2f}%")
    print(f"Precision : {precision_score(y_train, y_train_cv_pred)*100:.2f}%")
    print(f"Recall    : {recall_score(y_train, y_train_cv_pred)*100:.2f}%")
    print(f"F1-Score  : {f1_score(y_train, y_train_cv_pred)*100:.2f}%")

    # ---------- TRAIN FULL MODEL ----------
    model.fit(X_train, y_train)

    # ---------- TEST METRICS ----------
    y_test_pred = model.predict(X_test)

    print(f"{name} - TEST METRICS (HELD-OUT SET)")
    print(f"Accuracy  : {accuracy_score(y_test, y_test_pred)*100:.2f}%")
    print(f"Precision : {precision_score(y_test, y_test_pred)*100:.2f}%")
    print(f"Recall    : {recall_score(y_test, y_test_pred)*100:.2f}%")
    print(f"F1-Score  : {f1_score(y_test, y_test_pred)*100:.2f}%")

    test_f1 = f1_score(y_test, y_test_pred)

    if test_f1 > best_test_f1:
        best_test_f1 = test_f1
        best_model = model
        best_model_name = name

# =====================================================
# 5. SAVE MODEL
# =====================================================
joblib.dump(best_model, f"best_model_{best_model_name}.pkl")

print("\n" + "=" * 70)
print(f"✅ BEST MODEL       : {best_model_name}")
print(f"✅ Best Test F1     : {best_test_f1*100:.2f}%")
print(f"✅ Model saved as   : best_model_{best_model_name}.pkl")
