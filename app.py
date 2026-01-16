import streamlit as st
import pandas as pd
import joblib
import json
import lightgbm
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ================= STREAMLIT CONFIG =================
st.set_page_config(page_title="AI Diet Planner", layout="centered")
st.title("🥗 AI-ML Personalized Diet Plan Generator")
st.caption("LightGBM • Feature-Leakage Safe • Cloud Ready")

# ================= PATHS =================
MODEL_PATH = "diet_app/best_model_LightGBM.pkl"
TRAIN_PATH = "diet_app/train_data.csv"
INFER_PATH = "diet_app/final_unique_range_valid_medical_data.csv"
DIET_PATH = "diets/Actionable_Diet_Guidelines_from_TXT.json"

TARGET_COLUMN = "binary_diet"
LEAKAGE_COLUMNS = [
    "blood_sugar",
    "cholesterol",
    "hemoglobin",
    "alkaline_phosphatase",
    "cancer_severity_score",
    "diet_risk_score",
    "continuous_risk_score",
    "liver_risk_score"
]

# ================= LOAD MODEL =================
model = joblib.load(MODEL_PATH)

# ================= LOAD TRAIN DATA → FEATURE SCHEMA =================
train_df = pd.read_csv(TRAIN_PATH)
X_train = train_df.drop(columns=LEAKAGE_COLUMNS + [TARGET_COLUMN], errors="ignore")
FEATURE_COLUMNS = X_train.columns.tolist()

# ================= LOAD DIET RULES (ROBUST JSON HANDLING) =================
with open(DIET_PATH) as f:
    diet_data = json.load(f)

# If JSON is a list, convert to dict with keys "high_risk" and "low_risk"
if isinstance(diet_data, list):
    if len(diet_data) >= 2:
        diet_data = {"high_risk": diet_data[0], "low_risk": diet_data[1]}
    else:
        st.error("Diet JSON list must have at least 2 items.")
        st.stop()
elif not isinstance(diet_data, dict):
    st.error("Diet JSON must be a dictionary or list of at least 2 items.")
    st.stop()

# ================= LOAD INFERENCE DATA =================
infer_df = pd.read_csv(INFER_PATH)
st.subheader("📂 Medical Report Data")
st.dataframe(infer_df)

# ================= FEATURE ALIGNMENT FUNCTION =================
def prepare_features(df, feature_columns):
    return df.reindex(columns=feature_columns, fill_value=0)

# ================= PREDICTION =================
if st.button("🔍 Generate Diet Plan"):

    X = prepare_features(infer_df, FEATURE_COLUMNS)
    preds = model.predict(X)

    diet_keys = list(diet_data.keys())
    if len(diet_keys) < 2:
        st.error("Diet JSON must have at least two keys for mapping predictions.")
        st.stop()

    for i, pred in enumerate(preds):

        risk_label = "HIGH DIET RISK" if pred == 1 else "LOW DIET RISK"
        diet_key = diet_keys[0] if pred == 1 else diet_keys[1]
        diet_plan = diet_data[diet_key]

        st.divider()
        st.subheader(f"🧑 Patient {i+1}")
        st.write(f"**Diet Risk Classification:** {risk_label}")

        # ================= DISPLAY DIET PLAN =================
        for day, meals in diet_plan.items():
            st.markdown(f"### {day}")
            if isinstance(meals, dict):
                for meal, value in meals.items():
                    st.write(f"**{meal}:** {value}")
            elif isinstance(meals, list):
                for item in meals:
                    st.write(f"- {item}")
            else:
                st.write(meals)

        # ================= JSON EXPORT =================
        output = {
            "patient_data": infer_df.iloc[i].to_dict(),
            "predicted_binary_diet": int(pred),
            "risk_level": risk_label,
            "diet_plan": diet_plan
        }

        st.download_button(
            "⬇️ Download Diet Plan (JSON)",
            json.dumps(output, indent=4),
            file_name=f"patient_{i+1}_diet.json",
            mime="application/json",
            key=f"json_{i}"
        )

        # ================= PDF EXPORT =================
        def generate_pdf(condition, diet_plan, pid):
            file_name = f"patient_{pid}_{condition}_diet.pdf"
            doc = SimpleDocTemplate(file_name)
            styles = getSampleStyleSheet()
            content = []

            content.append(
                Paragraph(f"<b>Diet Plan for {condition}</b>", styles["Title"])
            )

            for day, meals in diet_plan.items():
                content.append(Paragraph(f"<b>{day}</b>", styles["Heading2"]))
                if isinstance(meals, dict):
                    for meal, value in meals.items():
                        content.append(Paragraph(f"{meal}: {value}", styles["Normal"]))
                elif isinstance(meals, list):
                    for item in meals:
                        content.append(Paragraph(f"- {item}", styles["Normal"]))
                else:
                    content.append(Paragraph(str(meals), styles["Normal"]))

            doc.build(content)
            return file_name

        pdf_file = generate_pdf(risk_label, diet_plan, i + 1)

        with open(pdf_file, "rb") as f:
            st.download_button(
                "⬇️ Download PDF",
                f,
                file_name=pdf_file,
                key=f"pdf_{i}"
            )

