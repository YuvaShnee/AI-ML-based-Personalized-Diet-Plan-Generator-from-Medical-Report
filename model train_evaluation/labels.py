import pandas as pd
import re

# load your zero-shot output
df = pd.read_csv("diet_predictions_fast_colab.csv")

def make_label(text):
    if not isinstance(text, str):
        text = ""

    t = text.lower()

    # diabetes
    if re.search(r"diabetes|diabetic|hyperglycemia", t):
        return "diabetic diet"

    # renal / kidney
    if re.search(r"renal|kidney|nephro|creatinine|urea", t):
        return "renal diet"

    # heart
    if re.search(r"cardiac|heart|myocardial|hypertension|bp", t):
        return "cardiac diet"

    # low salt
    if re.search(r"hypertension|blood pressure|htn|edema|ascites", t):
        return "low salt diet"

    # weight loss / obesity
    if re.search(r"obesity|overweight|bmi|fatty liver|weight reduction", t):
        return "weight loss diet"

    # high protein
    if re.search(r"malnutrition|protein energy|cancer|chemotherapy|burns|healing", t):
        return "high protein diet"

    # default
    return "balanced general diet"


# build combined text
df["combined_text"] = (
    df["diagnosis"].fillna("") + " " +
    df["clinical_notes"].fillna("") + " " +
    df["prescription"].fillna("")
)

# generate pseudo labels
df["rule_based_diet"] = df["combined_text"].apply(make_label)

print("Sample labels:")
print(df[["rule_based_diet", "predicted_diet"]].head())

# save optional
df.to_csv("diet_with_rule_labels.csv", index=False)
print("Saved diet_with_rule_labels.csv")
