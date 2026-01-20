import os

folders = [
    "output/clean_text",
    "output/json",
    "output/csv",
    "output/review_missing",
]

for f in folders:
    os.makedirs(f, exist_ok=True)

print("✅ All required folders created successfully!")


