import os
import re

DIR = "output/clean_text"

for txt_file in os.listdir(DIR):
    if not txt_file.endswith(".txt"):
        continue

    path = f"{DIR}/{txt_file}"

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    cleaned = re.sub(r"\s+", " ", text)
    cleaned = cleaned.strip()

    with open(path, "w", encoding="utf-8") as f:
        f.write(cleaned)

print("✅ Text cleaning completed!")
