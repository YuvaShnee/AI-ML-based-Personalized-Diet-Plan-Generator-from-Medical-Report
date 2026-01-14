
import streamlit as st
import os
import json

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Diet Guidelines Using Medical Reports",
    page_icon="🥗",
    layout="wide"
)

# ===================== LOAD RULE FILE =====================
@st.cache_data
def load_rules():
    if not os.path.exists("RuleBased_Diet_Plans.txt"):
        return []
    with open("RuleBased_Diet_Plans.txt", "r", encoding="utf-8") as f:
        return f.readlines()

diet_rules = load_rules()

# ===================== HTML + CSS + JS =====================
st.markdown("""
<!DOCTYPE html>
<html>
<head>
<style>
body {
    background: linear-gradient(120deg, #e3f2fd, #e8f5e9);
    font-family: 'Segoe UI', sans-serif;
}

/* Header */
.header {
    background: linear-gradient(90deg, #0d47a1, #1976d2);
    padding: 30px;
    border-radius: 18px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
}

/* Card */
.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
    margin-bottom: 25px;
}

/* Labels */
label {
    font-weight: 600;
}

/* Buttons */
button {
    background: linear-gradient(90deg, #2e7d32, #66bb6a);
    color: white;
    border: none;
    padding: 12px 22px;
    font-size: 16px;
    border-radius: 12px;
    cursor: pointer;
}

/* Diet items */
.diet-item {
    background: #f1f8e9;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}

/* Chat */
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

/* Footer */
.footer {
    text-align: center;
    color: #444;
    margin-top: 30px;
}
</style>
</head>
</html>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown("""
<div class="header">
    <h1>🥗 Diet Guidelines Using Medical Reports</h1>
    <p>Doctor-Oriented Rule-Based Nutrition Recommendation System</p>
</div>
""", unsafe_allow_html=True)

# ===================== DOCTOR INPUT PANEL =====================
st.markdown("<div class='card'><h3>👨‍⚕️ Patient Diagnosis Details</h3></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    patient_name = st.text_input("Patient Name", "John Doe")
    age = st.number_input("Age", 1, 120, 30)

with c2:
    gender = st.selectbox("Gender", ["Male", "Female"])
    diagnosis = st.selectbox(
        "Diagnosis",
        ["Diabetes", "Hypertension", "Heart Disease", "Obesity", "General"]
    )

with c3:
    severity = st.selectbox(
        "Severity Level",
        ["Mild", "Moderate", "Severe"]
    )

# ===================== GENERATE DIET =====================
if st.button("🧾 Generate Diet Guidelines"):
    st.markdown("<div class='card'><h3>🍽 Recommended Diet Guidelines</h3></div>", unsafe_allow_html=True)

    matched = False
    for rule in diet_rules:
        if diagnosis.lower() in rule.lower():
            st.markdown(f"<div class='diet-item'>✔ {rule.strip()}</div>", unsafe_allow_html=True)
            matched = True

    if not matched:
        st.markdown("<div class='diet-item'>✔ Balanced diet with fruits, vegetables, whole grains and low sugar intake.</div>", unsafe_allow_html=True)

# ===================== AI DIET CHAT =====================
st.markdown("<div class='card'><h3>🤖 AI Diet Assistant (Doctor Support)</h3></div>", unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = []

question = st.text_input("Ask diet-related questions (e.g., foods to avoid, meal timing)")

if st.button("💬 Ask AI"):
    if question:
        st.session_state.chat.append(("user", question))

        answer = "Maintain balanced meals with fruits, vegetables and adequate hydration."
        for rule in diet_rules:
            if any(word in rule.lower() for word in question.lower().split()):
                answer = rule.strip()
                break

        st.session_state.chat.append(("ai", answer))

for sender, msg in st.session_state.chat:
    if sender == "user":
        st.markdown(f"<div class='chat-user'><b>Doctor:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-ai'><b>AI:</b> {msg}</div>", unsafe_allow_html=True)

# ===================== FOOTER =====================
st.markdown("""
<div class="footer">
    🏥 Clinical Decision Support System | Streamlit Cloud Deployment
</div>
""", unsafe_allow_html=True)
