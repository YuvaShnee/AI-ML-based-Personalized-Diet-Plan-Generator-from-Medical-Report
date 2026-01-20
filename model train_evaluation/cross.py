import joblib
from sklearn.model_selection import cross_val_score
import numpy as np

# -----------------------------
# 1. Load saved model
# -----------------------------
model_path = "models/best_model_LightGBM.pkl"  # path to your saved model
best_model = joblib.load(model_path)

# -----------------------------
# 2. Evaluate train and test score
# -----------------------------
train_score = best_model.score(X_train, y_train) * 100
test_score = best_model.score(X_test, y_test) * 100

print(f"Train Score: {train_score:.2f}%")
print(f"Test Score : {test_score:.2f}%")

# -----------------------------
# 3. Cross-validation for mean and std
# -----------------------------
cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='f1')
cv_mean = np.mean(cv_scores) * 100
cv_std = np.std(cv_scores) * 100

print(f"CV F1-Score Mean: {cv_mean:.2f}%")
print(f"CV F1-Score Std : {cv_std:.2f}%")
