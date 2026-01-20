import pandas as pd
import re
from transformers import AutoTokenizer

# ---------- Step 1: Load and minimally clean text ----------
df = pd.read_csv("text_cleaned.csv")

text_columns = ["clinical_notes", "prescription", "diagnosis"]

def minimal_text_clean(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"[\n\r\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.encode("utf-8", "ignore").decode()
    return text.strip().lower()

for col in text_columns:
    if col in df.columns:
        df[col] = df[col].apply(minimal_text_clean)

# combine into one field
df["full_text"] = (
    df.get("diagnosis", "") + " " +
    df.get("clinical_notes", "") + " " +
    df.get("prescription", "")
).str.strip()

# ---------- Step 2: Tokenization ----------
model_name = "bert-base-uncased"  # or ClinicalBERT etc.

tokenizer = AutoTokenizer.from_pretrained(model_name)

texts = df["full_text"].fillna("").tolist()

encoded_inputs = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=256,
    return_tensors="pt"
)

print("Tokenization successful.")
print("Input IDs shape:", encoded_inputs['input_ids'].shape)
print("Attention mask shape:", encoded_inputs['attention_mask'].shape)

