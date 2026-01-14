import streamlit as st
import pandas as pd
import numpy as np
import joblib
from fpdf import FPDF
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI Diet Plan Generator",
    page_icon="🥗",
    layout="wide"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.main {
    background-color: #ffffff;
    padding: 2rem;
    border-radius: 12px;
}
h1 {
    color: #2c7be5;
}
.stButton>button {
    background-color: #2c7be5;
    color: white;
    border-radius: 8px;
    height: 45px;
    font-size: 16px;
}
.card {
    background-color: #f1f4f9;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.title("🥗 AI-ML Based Personalized Diet Plan Generator")
st.caption("Upload medical values → Predict health → Generate diet plan")

# ------------------ LOAD MODEL SAFELY ------------------
@st.cache_resource
def load_model():
    try:
        return joblib.load("best_model_LightGBM.pkl")
    except Exception as e:
        st.error("❌ Model failed to load. Please check LightGBM compatibility.")
        st.stop()

model = load_model()

# ------------------ LOAD DIET RULES ------------------
@st.cache_data
def load_diet_rules():
    if not os.path.exists("RuleBased_Diet_Plans.txt"):
        return "Diet rules file not found."
    with open("RuleBased_Diet_Plans.txt", "r", encoding="utf-8") as f:
        return f.read()

diet_rules = load_diet_rules()

# ------------------ USER INPUT ------------------
st.subheader("🧪 Enter Medical Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 1, 120, 30)
    bmi = st.number_input("BMI", 10.0, 60.0, 22.0)

with col2:
    glucose = st.number_input("Glucose Level", 50, 300, 110)
    bp = st.number_input("Blood Pressure", 50, 200, 80)

with col3:
    cholesterol = st.number_input("Cholesterol", 100, 400, 180)
    insulin = st.number_input("Insulin", 0, 300, 80)

# ------------------ PREDICTION ------------------
if st.button("🔍 Generate Diet Plan"):
    input_data = np.array([[age, bmi, glucose, bp, cholesterol, insulin]])

    try:
        prediction = model.predict(input_data)[0]
    except Exception as e:
        st.error("❌ Prediction failed due to model mismatch.")
        st.stop()

    st.success(f"✅ Health Category Predicted: **{prediction}**")

    # ------------------ DIET MATCHING ------------------
    st.subheader("🍽 Personalized Diet Recommendation")

    matched_plan = []
    for line in diet_rules.split("\n"):
        if prediction.lower() in line.lower():
            matched_plan.append(line)

    if matched_plan:
        for item in matched_plan:
            st.markdown(f"<div class='card'>🥗 {item}</div>", unsafe_allow_html=True)
    else:
        st.info("No specific diet found. Showing general healthy diet.")
        st.markdown(f"<div class='card'>{diet_rules}</div>", unsafe_allow_html=True)

    # ------------------ PDF EXPORT ------------------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Personalized Diet Plan", ln=True)
    pdf.cell(200, 10, f"Health Category: {prediction}", ln=True)

    for item in matched_plan:
        pdf.multi_cell(0, 8, item)

    pdf_path = "Diet_Plan.pdf"
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📄 Download Diet Plan (PDF)",
            data=f,
            file_name="Personalized_Diet_Plan.pdf",
            mime="application/pdf"
        )

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("🚀 Built with Streamlit Cloud | AI-ML Diet Recommendation System")





