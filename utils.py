import re

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def merge_inputs(diagnosis, notes, prescription):
    return clean_text(
        f"diagnosis {diagnosis} clinical notes {notes} prescription {prescription}"
    )

def post_process(predicted_label):
    DEFAULT_GUIDELINES = {
        "diabetes": {
            "diet_type": "Diabetic diet",
            "avoid": ["sugar", "white rice", "soft drinks"],
            "include": ["whole grains", "vegetables", "lean protein"]
        },
        "hypertension": {
            "diet_type": "Low sodium diet",
            "avoid": ["salt", "pickles", "processed food"],
            "include": ["fruits", "vegetables", "low-fat dairy"]
        }
    }

    return DEFAULT_GUIDELINES.get(
        predicted_label,
        {
            "diet_type": "Balanced diet",
            "avoid": ["junk food"],
            "include": ["fruits", "vegetables"]
        }
    )
