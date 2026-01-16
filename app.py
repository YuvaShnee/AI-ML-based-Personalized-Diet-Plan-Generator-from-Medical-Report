import streamlit as st
import pandas as pd
import joblib
import json
import lightgbm  # required for loading LightGBM pickle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ==================================================
# STREAMLIT PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="AI-ML Personalized Diet Planner",
    layout="centered"
)

st.title("🥗 AI-ML Based Personalized Diet Plan Generator")
st.caption("LightGBM Model + Rule-Based AI | Streamlit Cloud")

# ==================================================
# LOAD MODEL
# ==================================================
MODEL_PATH = "diet_app/best_model_LightGBM.pkl"
model = joblib.load(MODEL_PATH)

# ==================================================
# LOAD DIET GUIDELINES (JSON)
# ==================================================
DIET_JSON_PATH = "diets/Actionable_Diet_Guidelines_from_TXT.json"
with open(DIET_JSON_PATH, "r") as f:
    diet_data = json.load(f)

# ==================================================
# LABEL MAPPING
# ==================================================
label_map = {
    0: "diabetes",
    1: "hypertension",
    2: "thyroid",
    3: "vitamin deficiency"
}

# ==================================================
# LOAD MEDICAL CSV (AUTO)
# ==================================================
CSV_PATH = "diet_app/final_unique_range_valid_medical_data.csv"
df = pd.read_csv(CSV_PATH)

st.subheader("📂 Sample Medical Report (Auto Loaded)")
st.dataframe(df)

# ==================================================
# GENERATE DIET PLAN
# ==================================================
if st.button("🔍 Generate Diet Plan"):

    predictions = model.predict(df)

    for i, pred in enumerate(predictions):
        condition = label_map[int(pred)]
        diet_plan = diet_data[condition]

        st.divider()
        st.subheader(f"🧑 Patient {i + 1}")
        st.write(f"**Predicted Condition:** {condition.upper()}")

        # ---------------- DISPLAY DIET ----------------
        for day, meals in diet_plan.items():
            st.markdown(f"### {day}")
            for meal, value in meals.items():
                st.write(f"**{meal}:** {value}")

        # ---------------- JSON EXPORT ----------------
        result_json = {
            "patient_data": df.iloc[i].to_dict(),
            "predicted_condition": condition,
            "diet_plan": diet_plan
        }

        st.download_button(
            "⬇️ Download Diet Plan (JSON)",
            json.dumps(result_json, indent=4),
            file_name=f"patient_{i + 1}_diet.json",
            mime="application/json",
            key=f"json_{i}"
        )

        # ---------------- PDF GENERATION ----------------
        def generate_pdf(condition, diet_plan, pid):
            file_name = f"patient_{pid}_{condition}_diet.pdf"
            doc = SimpleDocTemplate(file_name)
            styles = getSampleStyleSheet()
            content = []

            content.append(
                Paragraph(f"<b>Diet Plan for {condition.upper()}</b>", styles["Title"])
            )

            for day, meals in diet_plan.items():
                content.append(Paragraph(f"<b>{day}</b>", styles["Heading2"]))
                for meal, value in meals.items():
                    content.append(Paragraph(f"{meal}: {value}", styles["Normal"]))

            doc.build(content)
            return file_name

        pdf_file = generate_pdf(condition, diet_plan, i + 1)

        with open(pdf_file, "rb") as f:
            st.download_button(
                "⬇️ Download Diet Plan (PDF)",
                f,
                file_name=pdf_file,
                key=f"pdf_{i}"
            )



