import streamlit as st
import pandas as pd
import joblib
import json
import lightgbm
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ================= STREAMLIT CONFIG =================
st.set_page_config(page_title="AI Diet Planner", layout="wide", page_icon="🥗")

# ================= SIDEBAR NAVIGATION =================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Dashboard", "About"])

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
train_df = pd.read_csv(TRAIN_PATH)
X_train = train_df.drop(columns=LEAKAGE_COLUMNS + [TARGET_COLUMN], errors="ignore")
FEATURE_COLUMNS = X_train.columns.tolist()

infer_df = pd.read_csv(INFER_PATH)

with open(DIET_PATH) as f:
    diet_data = json.load(f)
if isinstance(diet_data, list):
    if len(diet_data) >= 2:
        diet_data = {"high_risk": diet_data[0], "low_risk": diet_data[1]}
    else:
        st.error("Diet JSON list must have at least 2 items.")
        st.stop()
elif not isinstance(diet_data, dict):
    st.error("Diet JSON must be dict or list of 2 items.")
    st.stop()

# ================= FEATURE ALIGNMENT FUNCTION =================
def prepare_features(df, feature_columns):
    return df.reindex(columns=feature_columns, fill_value=0)

# ================= PREDICTION FUNCTION =================
def predict_risk(df):
    X = prepare_features(df, FEATURE_COLUMNS)
    preds = model.predict(X)
    df["risk_label"] = ["HIGH DIET RISK" if p==1 else "LOW DIET RISK" for p in preds]
    return df

# ================= PREDICTION =================
df_with_risk = predict_risk(infer_df)

# ================= HOME PAGE =================
if page == "Home":
    st.title("🏥 AI Diet Planner Home")
    st.markdown("""
    This AI-ML powered dashboard generates personalized diet plans for patients based on their medical data.
    Use the **Dashboard** to visualize patient risks and KPIs.
    """)
    st.subheader("📂 Medical Report Sample Data")
    st.dataframe(infer_df.head(10))

    # Option to generate diet plan
    if st.button("🔍 Generate Diet Plan for All Patients"):
        for i, pred in enumerate(df_with_risk["risk_label"]):
            diet_key = "high_risk" if pred=="HIGH DIET RISK" else "low_risk"
            diet_plan = diet_data[diet_key]

            st.divider()
            st.subheader(f"🧑 Patient {i+1}")
            st.write(f"**Diet Risk Classification:** {pred}")

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

# ================= DASHBOARD PAGE =================
elif page == "Dashboard":
    st.title("📊 Patient Dashboard")
    st.markdown("Visual summary of patient diet risk levels")

    # KPI cards
    total_patients = len(df_with_risk)
    high_risk = sum(df_with_risk["risk_label"]=="HIGH DIET RISK")
    low_risk = sum(df_with_risk["risk_label"]=="LOW DIET RISK")
    stable = total_patients - high_risk - low_risk  # example
    critical = high_risk  # example mapping

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Patients", total_patients)
    kpi2.metric("High Risk", high_risk)
    kpi3.metric("Low Risk", low_risk)
    kpi4.metric("Critical", critical)

    # Pie chart of risk distribution
    risk_counts = df_with_risk["risk_label"].value_counts().reset_index()
    risk_counts.columns = ["Risk", "Count"]
    fig = px.pie(risk_counts, names="Risk", values="Count", color="Risk",
                 color_discrete_map={"HIGH DIET RISK":"red","LOW DIET RISK":"green"})
    st.plotly_chart(fig, use_container_width=True)

    # Show raw data
    st.subheader("Patient Risk Table")
    st.dataframe(df_with_risk)

# ================= ABOUT PAGE =================
elif page == "About":
    st.title("ℹ️ About")
    st.markdown("""
    **AI Diet Planner** is a Streamlit application that:
    - Uses a LightGBM model to predict diet risk
    - Generates personalized diet plans
    - Visualizes high-risk vs low-risk patients
    - Provides KPI metrics and interactive charts

    **Features:**
    - JSON & PDF download for each patient
    - Interactive dashboard with pie chart and KPI cards
    - Sidebar navigation for multi-page layout

    Developed with Python, Streamlit, LightGBM, and Plotly.
    """)

