import pandas as pd
import re

# load your dataset (change path/column names if needed)
df = pd.read_csv("text_features_medical_filled.csv")

# columns that contain text
text_columns = [

    
    "clinical_notes",
    "prescription",
    "diagnosis"
]

def minimal_text_clean(text):
    if pd.isna(text):
        return ""

    # ensure string
    text = str(text)

    # remove newlines and tabs
    text = re.sub(r"[\n\r\t]+", " ", text)

    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    # remove weird/non-printable unicode characters
    text = text.encode("utf-8", "ignore").decode()

    # trim leading/trailing spaces
    text = text.strip()

    # lowercase (only if using uncased BERT; safe default)
    text = text.lower()

    return text


for col in text_columns:
    if col in df.columns:
        df[col] = df[col].apply(minimal_text_clean)

# optional: save cleaned file
df.to_csv("text_cleaned.csv", index=False)

print("Minimal text cleaning completed.")

