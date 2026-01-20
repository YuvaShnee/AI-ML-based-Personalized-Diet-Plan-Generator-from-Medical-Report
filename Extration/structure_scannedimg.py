import re
import json
import csv
from pathlib import Path

# --- Input / Output directories ---
IN_DIR = Path("output/clean_text_scanned_images")
OUT_JSON = Path("output/json/structured_all_reports.json")
OUT_CSV = Path("output/csv/structured_all_reports.csv")

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# ---- UNIVERSAL PATTERN DICTIONARY ----
PATTERNS = {
    # CBC / Hematology
    "hemoglobin": re.compile(r"Hemoglobin[:\s]*([0-9.]+)", re.IGNORECASE),
    "hematocrit_pcv": re.compile(r"(?:PCV|HCT|Packed Cell Volume)[^0-9]*([0-9.]+)", re.IGNORECASE),
    "rbc_count": re.compile(r"R\.?B\.?C\.?\s*Count[^0-9]*([0-9.]+)", re.IGNORECASE),
    "wbc_count": re.compile(r"(Total\s*WBC\s*Count|WBC\s*Count)[^\d]*([0-9]+)", re.IGNORECASE),
    "platelet_count": re.compile(r"Platelet\s*Count[^0-9]*([0-9]+)", re.IGNORECASE),
    "mcv": re.compile(r"MCV[^0-9]*([0-9.]+)", re.IGNORECASE),
    "mch": re.compile(r"MCH[^0-9]*([0-9.]+)", re.IGNORECASE),
    "mchc": re.compile(r"MCHC[^0-9]*([0-9.]+)", re.IGNORECASE),
    "neutrophils": re.compile(r"Neutrophils[^0-9]*([0-9.]+)", re.IGNORECASE),
    "lymphocytes": re.compile(r"Lymphocytes[^0-9]*([0-9.]+)", re.IGNORECASE),
    "eosinophils": re.compile(r"Eosinophils[^0-9]*([0-9.]+)", re.IGNORECASE),
    "monocytes": re.compile(r"Monocytes[^0-9]*([0-9.]+)", re.IGNORECASE),
    "crp": re.compile(r"(?:C[-\s]*Reactive\s*Protein|CRP)[^0-9]*([0-9.]+)", re.IGNORECASE),

    # --- LFT (Liver Function Test) ---
    "bilirubin_total": re.compile(r"Bilirubin\s*Total[^0-9]*([0-9.]+)", re.IGNORECASE),
    "bilirubin_direct": re.compile(r"(?:Conjugated|Direct|D\.?\s*Bilirubin)[^0-9]*([0-9.]+)", re.IGNORECASE),
    "bilirubin_indirect": re.compile(r"(?:Unconjugated|Indirect|I\.?\s*D\.?\s*Bilirubin)[^0-9]*([0-9.]+)", re.IGNORECASE),
    "sgot": re.compile(r"SGOT[^0-9]*([0-9.]+)", re.IGNORECASE),
    "sgpt": re.compile(r"SGPT[^0-9]*([0-9.]+)", re.IGNORECASE),
    "alkaline_phosphatase": re.compile(r"Alkaline\s*Phosphatase[^0-9]*([0-9.]+)", re.IGNORECASE),
    "total_protein": re.compile(r"Total\s*Protein[^0-9]*([0-9.]+)", re.IGNORECASE),
    "albumin": re.compile(r"Albumin[^0-9]*([0-9.]+)", re.IGNORECASE),
    "globulin": re.compile(r"Globulin[^0-9]*([0-9.]+)", re.IGNORECASE),
    "ag_ratio": re.compile(r"A\/G\s*Ratio[^0-9]*([0-9.]+)", re.IGNORECASE),
    "ggt": re.compile(r"(?:Gamma[\-\s]*GT|GGT|Gamma\s*Glutamyl\s*Transferase)[^0-9]*([0-9.]+)", re.IGNORECASE),

    # --- Optional tests ---
    "esr": re.compile(r"ESR[^0-9]*([0-9.]+)", re.IGNORECASE),
    "glucose": re.compile(r"(?:Glucose|Blood\s*Sugar)[^0-9]*([0-9.]+)", re.IGNORECASE),
}

# --- Helper to clean OCR text ---
def clean_text(text):
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    # Replace l -> 1 only if it is part of a number (e.g., "l2" -> "12")
    text = re.sub(r"(?<=\d)l(?=\d)", "1", text)
    return text

# --- Extract values ---
def extract_values(text):
    text = clean_text(text)
    extracted = {}
    for key, pattern in PATTERNS.items():
        match = pattern.search(text)
        value = match.group(match.lastindex) if match else ""
        extracted[key] = value.replace(",", "").strip() if value else ""
    return extracted

# --- Process all text files ---
all_data = []

for file in sorted(IN_DIR.glob("*.txt")):
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    record = extract_values(content)
    record["file_name"] = file.name
    all_data.append(record)

# --- Save JSON ---
with open(OUT_JSON, "w", encoding="utf-8") as jf:
    json.dump(all_data, jf, ensure_ascii=False, indent=2)

# --- Save CSV ---
columns = ["file_name"] + list(PATTERNS.keys())
with open(OUT_CSV, "w", newline="", encoding="utf-8") as cf:
    writer = csv.DictWriter(cf, fieldnames=columns)
    writer.writeheader()
    for row in all_data:
        writer.writerow(row)

print("✅ Extraction complete for all reports (CBC, CRP, LFT, etc.)")


