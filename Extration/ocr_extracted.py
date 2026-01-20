import pytesseract
from PIL import Image
import os

IMG_DIR = "data/scanned images"
OUT_DIR = "output/clean_text"

for img_file in os.listdir(IMG_DIR):
    if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    try:
        img_path = f"{IMG_DIR}/{img_file}"
        text = pytesseract.image_to_string(Image.open(img_path))

        out_path = f"{OUT_DIR}/{img_file}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"❌ Error processing {img_file} → {e}")

print("✅ OCR extraction completed!")
