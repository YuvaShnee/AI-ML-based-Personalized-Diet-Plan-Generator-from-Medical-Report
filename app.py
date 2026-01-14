
import streamlit as st
import os

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Diet Guidelines Using Medical Reports",
    page_icon="🥗",
    layout="wide"
)

# ================= STYLING =================
st.markdown("""
<style>
body { background-color: #f4f7fb; }
h1 { color: #1f4f82; font-weight: 800; }
.card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.highlight {
    background: linear-gradient(90deg,#27ae60,#2ecc71);
    color: white;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
}
.stButton>button {
    background-color: #1f77d0;
    color: white;
    height: 46px;
    border-radius: 10px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("🥗 Diet Guidelines Using Medical Reports")
st.caption("AI-assisted Personalized Nutrition Recommendation System")

# ================= LOAD RULE FILE =================
@st.cache_data
def load_rules():
    if not os.path.exists("RuleBased_Diet_Plans.txt"):
        return []
    with open("RuleBased_Diet_Plans.txt", "r", encoding="utf-8") as f:
        return f.readlines()

rules = load_rules()

# ================= INPUT =================
st.markdown("<div class='card'><h3>👤 Patient Details</h3></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    age = st.number_input("Age", 1, 120, 30)
with c2:
    gender = st.selectbox("Gender", ["Male", "Female"])
with c3:
    condition = st.selectbox(
        "Detected Medical Condition",
        ["Diabetes", "Hypertension", "Heart Disease", "General"]
    )

# ================= GENERATE =================
if st.button("🔍 Generate Diet Guidelines"):
    st.markdown("<div class='highlight'>Diet Guidelines Generated Successfully</div><br>", unsafe_allow_html=True)

    st.metric("Medical Condition", condition)

    st.markdown("<div class='card'><h3>🍽 Recommended Diet Plan</h3></div>", unsafe_allow_html=True)

    found = False
    for rule in rules:
        if condition.lower() in rule.lower():
            st.write("✔️", rule.strip())
            found = True

    if not found:
        st.write("✔️ Balanced diet with fruits, vegetables, low sugar, and adequate hydration.")
