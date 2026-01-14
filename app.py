import streamlit as st
import pickle
import numpy as np
import os

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Diet Guidelines Using Medical Reports",
    page_icon="🥗",
    layout="wide"
)

# =====================================================
# STYLING
# =====================================================
st.markdown("""
<style>
body {
    background-color: #f4f7fb;
}
h1 {
    color: #1f4f82;
    font-weight: 800;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 6px 15px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.highlight {
    background: linear-gradient(90deg,#27ae60,#2ecc71);
    color: white;
    padding: 15px;
    border-radius: 12px;
    font-weight: 600;
}
.stButton>button {
    background-color: #1f77d0;
    color: white;
    border-radius: 8px;
    height: 45px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================
st.title("🥗 Diet Guidelines Using Medical Reports")
st.caption("AI-based Personalized Diet Recommendation System")

# =====================================================
# LOAD MODEL (PICKLE ONLY)
# =====================================================
@st.cache_resource
def load_model():
    with open("best_model_LightGBM.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

# =====================================================
# LOAD DIET RULES
# =====================================================
@st.cache_data
def load_rules():
    if not os.path.exists("RuleBased_Diet_Plans.txt"):
        return []
    with open("RuleBased_Diet_Plans.txt", "r", encoding="utf-8") as f:
        return f.readlines()

diet_rules = load_rules()

# =====================================================
# INPUT SECTION
# =====================================================
st.markdown("<div class='card'><h3>🧪 Patient Medical Inputs</h3></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    age = st.number_input("Age", 1, 120, 30)
    bmi = st.number_input("BMI", 10.0, 60.0, 22.0)

with c2:
    glucose = st.number_input("Glucose Level", 50, 300, 110)
    bp = st.number_input("Blood Pressure", 50, 200, 80)

with c3:
    cholesterol = st.number_input("Cholesterol", 100, 400, 180)
    insulin = st.number_input("Insulin", 0, 300, 80)

# =====================================================
# PREDICTION
# =====================================================
if st.button("🔍 Generate Diet Guidelines"):
    X = np.array([[age, bmi, glucose, bp, cholesterol, insulin]])

    prediction = model.predict(X)[0]

    st.markdown("<div class='highlight'>Prediction Completed Successfully</div><br>", unsafe_allow_html=True)

    st.metric("Predicted Health Condition", prediction)

    # =================================================
    # MATCH DIET RULES
    # =================================================
    st.markdown("<div class='card'><h3>🍽 Recommended Diet Plan</h3></div>", unsafe_allow_html=True)

    matched = False
    for rule in diet_rules:
        if str(prediction).lower() in rule.lower():
            st.write("✔️", rule.strip())
            matched = True

    if not matched:
        st.write("✔️ Follow a balanced diet with fruits, vegetables, and low sugar intake.")
