import streamlit as st
import pickle
import json
import pandas as pd
import numpy as np

# Optional imports
try:
    import lightgbm as lgb
    lightgbm_available = True
except ModuleNotFoundError:
    lightgbm_available = False
    st.error("LightGBM is not installed. Prediction will not work.")

try:
    import shap
    shap_available = True
except ModuleNotFoundError:
    shap_available = False

try:
    import matplotlib.pyplot as plt
    matplotlib_available = True
except ModuleNotFoundError:
    matplotlib_available = False

try:
    from fpdf import FPDF
    fpdf_available = True
except ModuleNotFoundError:
    fpdf_available = False

try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    sklearn_available = True
except ModuleNotFoundError:
    sklearn_available = False

# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="AI Diet Recommendation System",
    page_icon="🥗",
    layout="wide"
)

# =========================================================
# Custom CSS
# =========================================================
st.markdown("""
<style>
body { background-color: #f6f8fb; }
h1 { color: #2c3e50; font-weight: 700; }
h2, h3 { color: #34495e; }
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.stButton>button {
    background-color: #27ae60;
    color: white;
    font-size: 16px;
    border-radius: 8px;
    height: 3em;
}
.stDownloadButton>button {
    background-color: #2980b9;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# Load ML Model (LightGBM)
# =========================================================
if lightgbm_available:
    try:
        with open("best_model_LightGBM.pkl", "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        st.error(f"Failed to load LightGBM model: {e}")
        model = None
else:
    model = None

# =========================================================
# Helper Functions
# =========================================================
def extract_features(text, age, gender):
    gender_val = 1 if gender == "Male" else 0
    return [len(text), age, gender_val]

def generate_diet(condition):
    plans = {
        "diabetes": {
            "diet_type": "Diabetic Diet",
            "plan": [
                "Breakfast: Oatmeal with skim milk",
                "Lunch: Quinoa salad with legumes",
                "Snack: Apple slices, almonds",
                "Dinner: Steamed fish and vegetables"
            ]
        },
        "hypertension": {
            "diet_type": "Low Sodium Diet",
            "plan": [
                "Breakfast: Fruits with oats",
                "Lunch: Brown rice with vegetables",
                "Snack: Unsalted nuts",
                "Dinner: Grilled chicken salad"
            ]
        }
    }
    return plans.get(condition, {
        "diet_type": "Balanced Diet",
        "plan": [
            "Breakfast: Fruits and nuts",
            "Lunch: Home-cooked vegetables",
            "Dinner: Light meal"
        ]
    })

def generate_pdf(patient, condition, diet):
    if not fpdf_available:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Patient Name: {patient}", ln=True)
    pdf.cell(0, 10, f"Medical Condition: {condition}", ln=True)
    pdf.cell(0, 10, f"Diet Type: {diet['diet_type']}", ln=True)
    pdf.ln(5)
    for item in diet["plan"]:
        pdf.multi_cell(0, 8, f"- {item}")
    return pdf.output(dest="S").encode("latin-1")

# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("🥗 AI Diet System")
st.sidebar.info("""
• ML-based prediction  
• Actionable diet plans  
• PDF & JSON export  
• Metrics dashboard  
• Explainable AI  
""")

# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3 = st.tabs(["🧠 Prediction", "📊 Metrics", "🔍 Explainable AI"])

# =========================================================
# TAB 1: Prediction
# =========================================================
with tab1:
    st.markdown("<div class='card'><h2>Patient Input</h2></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        patient_name = st.text_input("Patient Name")
    with col2:
        age = st.number_input("Age", 1, 100, 30)
    with col3:
        gender = st.selectbox("Gender", ["Male", "Female"])

    uploaded_file = st.file_uploader("Upload Doctor Notes (TXT)", type=["txt"])

    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")

        with st.expander("View Uploaded Text"):
            st.text(text)

        X = np.array([extract_features(text, age, gender)])

        if model is not None:
            prediction = model.predict(X)[0]
            diet = generate_diet(prediction)

            st.markdown("<div class='card'><h2>Generated Diet Plan</h2></div>", unsafe_allow_html=True)
            st.metric("Predicted Condition", prediction)
            st.metric("Diet Type", diet["diet_type"])
            for item in diet["plan"]:
                st.write("•", item)

            # JSON download
            json_data = {
                "patient": patient_name,
                "condition": prediction,
                "diet_type": diet["diet_type"],
                "diet_plan": diet["plan"]
            }

            colA, colB = st.columns(2)
            with colA:
                st.download_button("⬇ Download JSON", json.dumps(json_data, indent=2),
                                   "diet_plan.json", "application/json")
            with colB:
                if fpdf_available:
                    pdf_data = generate_pdf(patient_name or "Patient", prediction, diet)
                    st.download_button("⬇ Download PDF", pdf_data,
                                       "diet_plan.pdf", "application/pdf")
        else:
            st.warning("Prediction unavailable because LightGBM is not installed.")

# =========================================================
# TAB 2: Metrics Dashboard
# =========================================================
with tab2:
    if sklearn_available:
        st.markdown("<div class='card'><h2>Model Evaluation Metrics</h2></div>", unsafe_allow_html=True)

        eval_file = st.file_uploader(
            "Upload Evaluation CSV (true_label, predicted_label)",
            type=["csv"],
            key="metrics"
        )

        if eval_file:
            df = pd.read_csv(eval_file)
            y_true = df["true_label"]
            y_pred = df["predicted_label"]

            acc = accuracy_score(y_true, y_pred)
            prec = precision_score(y_true, y_pred, average="weighted")
            rec = recall_score(y_true, y_pred, average="weighted")
            f1 = f1_score(y_true, y_pred, average="weighted")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", f"{acc*100:.2f}%")
            c2.metric("Precision", f"{prec*100:.2f}%")
            c3.metric("Recall", f"{rec*100:.2f}%")
            c4.metric("F1 Score", f"{f1*100:.2f}%")

# =========================================================
# TAB 3: Explainable AI (Optimized)
# =========================================================
with tab3:
    if shap_available and matplotlib_available and 'X' in locals():
        explainer = shap.TreeExplainer(model) if model is not None else None
        if explainer is not None:
            shap_values = explainer.shap_values(X)
            shap_abs = np.abs(shap_values).mean(axis=0)

            features = ["Text Length", "Age", "Gender"]
            fig, ax = plt.subplots()
            ax.barh(features, shap_abs, color="#27ae60")
            ax.set_xlabel("Mean |SHAP value|")
            ax.set_title("Feature Importance (Patient-level)")
            plt.gca().invert_yaxis()
            st.pyplot(fig)
        else:
            st.warning("Explainable AI unavailable because LightGBM model is missing.")




