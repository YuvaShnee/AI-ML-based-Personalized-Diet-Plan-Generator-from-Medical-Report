import pytesseract
from PIL import Image
from pathlib import Path
import re
from tqdm import tqdm  # for progress bar

# --- Paths ---
INPUT_DIR = Path("data/scanned images")       # folder containing scanned images
OUTPUT_DIR = Path("output/clean_text_scanned_images")  # folder to save cleaned text
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Tesseract path (update if needed) ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- Clean text function ---
def clean_text(text):
    text = re.sub(r"\s+", " ", text)  # normalize spaces
    text = re.sub(r"(?<=\d)l(?=\d)", "1", text)  # fix OCR 'l' in numbers
    return text.strip()

# --- Process images ---
image_files = [f for f in INPUT_DIR.glob("*.*") if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]]

for img_file in tqdm(image_files, desc="Processing scanned images"):
    try:
        img = Image.open(img_file)
        raw_text = pytesseract.image_to_string(img, lang="eng")
        cleaned_text = clean_text(raw_text)
        
        out_file = OUTPUT_DIR / f"{img_file.stem}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
    except Exception as e:
        print(f"⚠️ Failed to process {img_file.name}: {e}")

print(f"✅ Completed OCR and cleaned text for {len(image_files)} images.")

