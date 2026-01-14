

import streamlit as st
import pandas as pd
import os
import re

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Diet Guidelines Using Medical Reports",
    page_icon="🥗",
    layout="wide"
)

# =====================================================
# GLOBAL CSS (WEBSITE STYLE)
# =====================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2f3, #ffffff);
    font-family: 'Segoe UI', sans-serif;
}
.hero {
    background: linear-gradient(90deg, #0f4c81, #1e88e5);
    color: white;
    padding: 35px;
    border-radius: 20px;
    margin-bottom: 30px;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.kpi {
    background: #f4f8ff;
    padding: 18px;
    border-radius: 14px;
    text-align: center;
}
.chat-user {
    background: #e3f2fd;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.chat-ai {
    background: #e8f5e9;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.stButton>button {
    background: linear-gradient(90deg,#1565c0,#42a5f5);
    color: white;
    height: 46px;
    border-radius: 10px;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="hero">
    <h1>🥗 Diet Guidelines Using Medical Reports</h1>
    <p>Doctor-oriented rule-based nutrition recommendation system</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DIET RULES
# =====================================================
@st.cache_data
def load_rules():
    rules = {}
    with open("RuleBased_Diet_Plans.txt", "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                k, v = line.split(":", 1)
                rules[k.strip().lower()] = v.strip()
    return rules

diet_rules = load_rules()

# =====================================================
# PARSE DOCTOR NOTES
# =====================================================
def parse_doctor_notes(text):
    name = re.search(r"name[:\-]\s*(.*)", text, re.I)
    age = re.search(r"age[:\-]\s*(\d+)", text, re.I)
    gender = re.search(r"gender[:\-]\s*(male|female)", text, re.I)
    diagnosis = re.search(r"(diabetes|hypertension|heart disease|obesity)", text, re.I)

    return {
        "Name": name.group(1) if name else "Unknown",
        "Age": int(age.group(1)) if age else None,
        "Gender": gender.group(1).title() if gender else "Unknown",
        "Diagnosis": diagnosis.group(1).title() if diagnosis else "General"
    }

# =====================================================
# UPLOAD DOCTOR NOTES
# =====================================================
st.markdown("<div class='card'><h3>📄 Upload Doctor Notes</h3></div>", unsafe_allow_html=True)
uploaded = st.file_uploader("Upload .txt medical report", type=["txt"])

patients = []

if uploaded:
    text = uploaded.read().decode("utf-8")
    data = parse_doctor_notes(text)
    patients.append(data)

# =====================================================
# PATIENT TABLE
# =====================================================
if patients:
    df = pd.DataFrame(patients)

    st.markdown("<div class='card'><h3>👥 Patient Records</h3></div>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

    # =================================================
    # DASHBOARD
    # =================================================
    st.markdown("<div class='card'><h3>📊 Health Dashboard</h3></div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='kpi'><h4>Diabetes</h4><h2>{(df['Diagnosis']=='Diabetes').sum()}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi'><h4>Hypertension</h4><h2>{(df['Diagnosis']=='Hypertension').sum()}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='kpi'><h4>Heart Disease</h4><h2>{(df['Diagnosis']=='Heart Disease').sum()}</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='kpi'><h4>Obesity</h4><h2>{(df['Diagnosis']=='Obesity').sum()}</h2></div>", unsafe_allow_html=True)

    # =================================================
    # DIET PLAN
    # =================================================
    st.markdown("<div class='card'><h3>🍽 Recommended Diet</h3></div>", unsafe_allow_html=True)
    diag = df.iloc[0]["Diagnosis"].lower()
    st.success(diet_rules.get(diag, diet_rules.get("general")))

# =====================================================
# AI CHAT (RULE + NOTES BASED)
# =====================================================
st.markdown("<div class='card'><h3>🤖 AI Diet Assistant</h3></div>", unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = []

question = st.text_input("Ask about diet, food restrictions, meals, etc.")

if st.button("Ask AI"):
    if question:
        st.session_state.chat.append(("user", question))
        answer = diet_rules.get("general")

        for key in diet_rules:
            if key in question.lower():
                answer = diet_rules[key]
                break

        st.session_state.chat.append(("ai", answer))

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='chat-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-ai'><b>AI:</b> {msg}</div>", unsafe_allow_html=True)
