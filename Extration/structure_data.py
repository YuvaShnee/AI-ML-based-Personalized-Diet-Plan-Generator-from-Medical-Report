

import re
import json
import csv
from pathlib import Path
import pdfplumber

PDF_DIR = Path("data/doctor_prescription_reports_400")
OUT_JSON = Path("output/json/structured_data.json")
OUT_CSV = Path("output/csv/structured_data.csv")
OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

PATTERNS = {
    "patient_name": re.compile(r"Patient Name[:\s]*([^\n\r]+)", re.IGNORECASE),
    "age": re.compile(r"Age[:\s]*([0-9]{1,3})", re.IGNORECASE),
    "bmi": re.compile(r"BMI[:\s]*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
    "cholesterol": re.compile(r"Cholesterol[:\s]*([0-9]+)", re.IGNORECASE),
    "blood_sugar": re.compile(r"Blood Sugar[:\s]*([0-9]+)", re.IGNORECASE),
    "diagnosis": re.compile(r"Diagnosis[:\s]*([^\n\r]+)", re.IGNORECASE),
    "prescription_block": re.compile(r"Prescription[:\s]*\n([\s\S]+)", re.IGNORECASE)
}

def extract_fields(text):
    data = {}
    for key, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            data[key] = match.group(1).strip()
        else:
            data[key] = ""

    # Split prescription into items
    pres_items = []
    if data["prescription_block"]:
        for line in data["prescription_block"].splitlines():
            line = line.strip()
            if re.match(r"^\d+\)", line):
                pres_items.append(line.split(")",1)[1].strip())
    data["prescription"] = pres_items
    data.pop("prescription_block", None)
    return data

all_data = []

for pdf_file in sorted(PDF_DIR.glob("*.pdf")):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        record = extract_fields(text)
        record["file"] = pdf_file.name
        all_data.append(record)

# Save JSON
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

# Save CSV
keys = ["file", "patient_name", "age", "bmi", "cholesterol", "blood_sugar", "diagnosis", "prescription"]
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    for row in all_data:
        row_copy = row.copy()
        row_copy["prescription"] = "; ".join(row_copy["prescription"])
        writer.writerow(row_copy)

print("✅ Extraction complete. Check output CSV and JSON.")
