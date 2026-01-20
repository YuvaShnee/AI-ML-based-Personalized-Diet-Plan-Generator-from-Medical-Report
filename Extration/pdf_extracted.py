# pdf_extract.py
import os
from pathlib import Path
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

IN_DIR = Path("data/doctor_prescription_reports_400")
OUT_DIR = Path("output/clean_text")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"
    return text.strip()

def main():
    pdf_files = list(IN_DIR.glob("*.pdf"))
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        try:
            text = extract_text_from_pdf(pdf_file)
            # If no text found, fallback to OCR
            if len(text) < 30:
                text = extract_text_with_ocr(pdf_file)
            
            out_path = OUT_DIR / f"{pdf_file.stem}.txt"
            out_path.write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

    print(f"✅ Text extraction complete! Saved to {OUT_DIR}")

if __name__ == "__main__":
    main()

