
import streamlit as st
import pandas as pd
import os

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Diet Guidelines Using Medical Reports",
    page_icon="🥗",
    layout="wide"
)

# ================== WEBSITE CSS ==================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg,#eef2f3,#d9e4f5);
}
.header {
    background: linear-gradient(90deg,#0f2027,#203a43,#2c5364);
    padding: 35px;
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
}
.section {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}
.stat {
    background: #f1f5ff;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
.chat-user {
    background:#e3f2fd;
    padding:12px;
    border-radius:14px;
    margin:8px 0;
}
.chat-ai {
    background:#e8f5e9;
    padding:12px;
    border-radius:14px;
    margin:8px 0;
}
.stButton>button {
    background: linear-gradient(90deg,#1565c0,#42a5f5);
    color:white;
    border-radius:12px;
    height:48px;
    font-size:16px;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("""
<div class="header">
<h1>🥗 Diet Guidelines Using Medical Reports</h1>
<p>Doctor-Oriented Rule-Based Nutrition Recommendation System</p>
</div>
""", unsafe_allow_html=True)

# ================== LOAD DIET RULES ==================
@st.cache_data
def load_rules():
    rules = {}
    with open("RuleBased_Diet_Plans.txt", "r") as f:
        for line in f:
            if ":" in line:
                cond, text = line.split(":", 1)
                rules.setdefault(cond.strip(), []).append(text.strip())
    return rules

diet_rules = load_rules()

# ================== PATIENT DATABASE ==================
if "patients" not in st.session_state:
    st.session_state.patients = []

# ================== PATIENT ENTRY ==================
st.markdown("<div class='section'><h3>👤 Patient Diagnosis Entry</h3></div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    name = st.text_input("Patient Name")
with c2:
    age = st.number_input("Age", 1, 120, 30)
with c3:
    gender = st.selectbox("Gender", ["Male", "Female"])
with c4:
    diagnosis = st.selectbox(
        "Diagnosis",
        ["diabetes", "hypertension", "heart disease", "obesity"]
    )

if st.button("➕ Add Patient"):
    st.session_state.patients.append({
        "Name": name,
        "Age": age,
        "Gender": gender,
        "Diagnosis": diagnosis
    })
    st.success("Patient added successfully")

# ================== DASHBOARD ==================
st.markdown("<div class='section'><h3>📊 Patient Dashboard</h3></div>", unsafe_allow_html=True)

df = pd.DataFrame(st.session_state.patients)

if not df.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Diabetes", (df["Diagnosis"]=="diabetes").sum())
    c2.metric("Hypertension", (df["Diagnosis"]=="hypertension").sum())
    c3.metric("Heart Disease", (df["Diagnosis"]=="heart disease").sum())
    c4.metric("Obesity", (df["Diagnosis"]=="obesity").sum())

    st.dataframe(df, use_container_width=True)

# ================== DIET GUIDELINES ==================
st.markdown("<div class='section'><h3>🍽 Recommended Diet Guidelines</h3></div>", unsafe_allow_html=True)

if not df.empty:
    selected = st.selectbox("Select Patient", df["Name"])
    condition = df[df["Name"] == selected]["Diagnosis"].values[0]

    for rule in diet_rules.get(condition, []):
        st.success(rule)

# ================== AI CHAT ==================
st.markdown("<div class='section'><h3>🤖 AI Diet Assistant</h3></div>", unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = []

question = st.text_input("Ask diet questions based on medical reports")

if st.button("Ask AI"):
    st.session_state.chat.append(("user", question))
    answer = "Maintain balanced nutrition and hydration."
    for cond, rules in diet_rules.items():
        if cond in question.lower():
            answer = rules[0]
            break
    st.session_state.chat.append(("ai", answer))

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='chat-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-ai'><b>AI:</b> {msg}</div>", unsafe_allow_html=True)
