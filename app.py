import streamlit as st
import pandas as pd
import joblib
import json
import lightgbm
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ==================================================
# STREAMLIT CONFIG
# ==================================================
st.set_page_config(page_title="AI Diet Planner", layout="centered")
st.title("🥗 AI-ML Based Personalized Diet Plan Generator")
st.caption("LightGBM + Medical Report Analysis")

# ==================================================
# PATHS
# ==================================================
MODEL_PATH = "diet_app/best_model_LightGBM.pkl"
TRAIN_PATH = "diet_app/train_data.csv"
INFER_PATH = "diet_app/final_unique_range_valid_medical_data.csv"
DIET_PATH = "diets/Actionable_Diet_Guidelines_from_TXT.json"

# ==================================================
# LOAD MODEL
# ==================================================
model = joblib.load(MODEL_PATH)

# ==================================================
# LOAD TRAIN DATA → FEATURE SCHEMA
# ==================================================
train_df = pd.read_csv(TRAIN_PATH)

TARGET_COLUMN = "medical_condition"  # 🔴 CHANGE ONLY IF YOUR TARGET NAME IS DIFFERENT

X_train = train_df.drop(columns=[TARGET_COLUMN])
FEATURE_COLUMNS = X_train.columns.tolist()

# ==================================================
# LOAD DIET RULES
# ==================================================
with open(DIET_PATH) as f:
    diet_data = json.load(f)

# ==================================================
# LABEL MAP (MATCH TRAINING)
# ==================================================
label_map = {
    0: "diabetes",
    1: "hypertension",
    2: "thyroid",
    3: "vitamin deficiency"
}

# ==================================================
# FEATURE ALIGNMENT FUNCTION
# ==================================================
def align_features(df, feature_columns):
    return df.reindex(columns=feature_columns, fill_value=0)

# ==================================================
# LOAD INFERENCE CSV
# ==================================================
infer_df = pd.read_csv(INFER_PATH)
st.subheader("📂 Medical Report Data")
st.dataframe(infer_df)

# ==================================================
# PREDICTION
# ==================================================
if st.button("🔍 Generate Diet Plan"):

    aligned_df = align_features(infer_df, FEATURE_COLUMNS)
    predictions = model.predict(aligned_df)

    for i, pred in enumerate(predictions):
        condition = label_map[int(pred)]
        diet_plan = diet_data[condition]

        st.divider()
        st.subheader(f"🧑 Patient {i+1}")
        st.write(f"**Predicted Condition:** {condition.upper()}")

        for day, meals in diet_plan.items():
            st.markdown(f"### {day}")
            for meal, value in meals.items():
                st.write(f"**{meal}:** {value}")

        # ================= JSON EXPORT =================
        result_json = {
            "patient_data": infer_df.iloc[i].to_dict(),
            "predicted_condition": condition,
            "diet_plan": diet_plan
        }

        st.download_button(
            "⬇️ Download JSON",
            json.dumps(result_json, indent=4),
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
                "⬇️ Download PDF",
                f,
                file_name=pdf_file,
                key=f"pdf_{i}"
            )




