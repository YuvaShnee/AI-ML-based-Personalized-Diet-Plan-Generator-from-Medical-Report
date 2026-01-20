import re
import json
import pandas as pd

INPUT_CSV =("output/csv/tcga_clean.csv")
OUT_JSON = "tcga_structured.json"
OUT_CSV = "tcga_structured.csv"


def extract_field(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def structure_text(text):
    data = {}

    # --- Basic Fields ---
    data["patient_id"] = extract_field(r"Patient ID[:\-]\s*(.*?)\n", text)
    data["age"] = extract_field(r"Age[:\-]\s*(\d+)", text)
    data["gender"] = extract_field(r"\b(Male|Female)\b", text)

    # --- Clinical Information ---
    data["specimen"] = extract_field(r"Specimen[:\-]\s*(.*)", text)
    data["material"] = extract_field(r"Material[:\-]\s*(.*)", text)
    data["clinical_notes"] = extract_field(r"Clinical(?: Notes| History)?[:\-]\s*(.*)", text)

    # --- Diagnosis / Pathology ---
    data["histopathology_diagnosis"] = extract_field(r"Diagnosis[:\-]\s*(.*)", text)
    data["gross_description"] = extract_field(r"Gross Description[:\-]\s*(.*)", text)
    data["microscopic_description"] = extract_field(r"Microscopic(?: Description)?[:\-]\s*(.*)", text)

    # --- Tumor Information ---
    data["tumor_size"] = extract_field(r"Tumou?r Size[:\-]\s*(.*)", text)
    data["tumor_grade"] = extract_field(r"Grade[:\-]\s*(.*)", text)
    data["lymph_nodes"] = extract_field(r"Lymph Nodes[:\-]\s*(.*)", text)
    data["stage"] = extract_field(r"Stage[:\-]\s*(.*)", text)

    return data


# --- Load Input CSV ---
df = pd.read_csv(INPUT_CSV)

structured_rows = []

for _, row in df.iterrows():
    clean_text = str(row["text"])
    record = structure_text(clean_text)
    record["file"] = row["patient_filename"]
    structured_rows.append(record)


# --- Save JSON ---
with open(OUT_JSON, "w", encoding="utf-8") as jf:
    json.dump(structured_rows, jf, indent=4)


# --- Save CSV ---
out_df = pd.DataFrame(structured_rows)
out_df.to_csv(OUT_CSV, index=False)

print("✅ Structured TCGA data saved as CSV & JSON!")
