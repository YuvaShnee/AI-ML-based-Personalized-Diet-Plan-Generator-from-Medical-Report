import pandas as pd
from sklearn.model_selection import train_test_split

# ---------------------------------
# 1. Load dataset with target
# ---------------------------------
df = pd.read_csv("final_preprocessed_with_target.csv")

# ---------------------------------
# 2. Define features and target
# ---------------------------------
target_column = "binary_diet"

X = df.drop(columns=[target_column])
y = df[target_column]

# ---------------------------------
# 3. Train-Test Split (80-20)
# ---------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ---------------------------------
# 4. Save to CSV files
# ---------------------------------
train_df = pd.concat([X_train, y_train], axis=1)
test_df = pd.concat([X_test, y_test], axis=1)

train_df.to_csv("train_data.csv", index=False)
test_df.to_csv("test_data.csv", index=False)

# ---------------------------------
# 5. Verify split
# ---------------------------------
print("✅ Train/Test split completed")
print("Train shape:", train_df.shape)
print("Test shape :", test_df.shape)

print("\nTrain class distribution:")
print(train_df[target_column].value_counts(normalize=True) * 100)

print("\nTest class distribution:")
print(test_df[target_column].value_counts(normalize=True) * 100)


