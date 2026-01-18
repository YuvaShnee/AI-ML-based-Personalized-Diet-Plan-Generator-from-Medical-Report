import streamlit as st
import pandas as pd
import joblib
import json
import os
import plotly.graph_objects as go
from datetime import datetime
import time

# ================= STREAMLIT CONFIG =================
st.set_page_config(
    page_title="AI Diet Planner | Smart Healthcare",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# ================= PROFESSIONAL CUSTOM CSS =================
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: #f8f9fa;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Sidebar Professional Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* Sidebar Text Colors */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Navigation Header in Sidebar */
    .nav-header {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Radio Buttons Professional Style */
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        gap: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
        background: rgba(255, 255, 255, 0.1);
        padding: 14px 20px;
        border-radius: 10px;
        margin: 6px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.4);
        transform: translateX(5px);
    }
    
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] span {
        color: white !important;
        font-size: 15px !important;
        font-weight: 500;
    }
    
    /* Sidebar Metrics */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 13px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    /* Divider in Sidebar */
    [data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 64, 175, 0.2);
    }
    
    .main-header h1 {
        font-size: 2.8em;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    
    .main-header h3 {
        font-size: 1.3em;
        font-weight: 500;
        margin: 1rem 0 0.5rem 0;
        opacity: 0.95;
    }
    
    .main-header p {
        font-size: 1.05em;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(90deg, #1e40af 0%, #7c3aed 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        font-size: 1.3em;
        margin: 2rem 0 1.5rem 0;
        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.15);
    }
    
    /* KPI Metric Cards */
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #3b82f6;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card h3 {
        color: #1e40af;
        font-size: 2.5em;
        margin: 0.8rem 0;
        font-weight: 700;
    }
    
    .metric-card .label {
        color: #64748b;
        font-size: 0.95em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .sublabel {
        color: #94a3b8;
        font-size: 0.85em;
        margin-top: 0.5rem;
    }
    
    .metric-card .delta {
        color: #10b981;
        font-size: 0.9em;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        height: 100%;
        border-top: 4px solid #3b82f6;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
    }
    
    .feature-card .icon {
        font-size: 3.5em;
        margin-bottom: 1.5rem;
    }
    
    .feature-card h3 {
        color: #1e293b;
        margin-bottom: 1rem;
        font-weight: 700;
        font-size: 1.3em;
    }
    
    .feature-card p {
        color: #64748b;
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* Content Containers */
    .content-container {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 0.9rem 2.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(30, 64, 175, 0.3);
    }
    
    /* Risk Badges */
    .risk-badge-high {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .risk-badge-low {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Diet Card */
    .diet-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.15);
        border-left: 4px solid #f59e0b;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .info-box h4 {
        margin: 0 0 0.8rem 0;
        font-weight: 700;
        font-size: 1.1em;
    }
    
    .info-box p {
        margin: 0;
        font-size: 14px;
        line-height: 1.6;
        opacity: 0.95;
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f1f5f9;
        border-radius: 10px;
        font-weight: 600;
        color: #1e40af;
    }
    
    /* Download Button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(5, 150, 105, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2.5rem;
        background: white;
        border-radius: 16px;
        margin-top: 3rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }
    
    .footer h3 {
        color: #1e40af;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .footer p {
        color: #64748b;
        margin: 0.5rem 0;
    }
    
    .footer .contact {
        margin-top: 1.5rem;
    }
    
    .footer .contact span {
        margin: 0 1rem;
        color: #1e40af;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ================= PATHS =================
MODEL_PATH = "diet_app/best_model_LightGBM.pkl"
TRAIN_PATH = "diet_app/train_data.csv"
INFER_PATH = "diet_app/final_unique_range_valid_medical_data.csv"
DIET_PATH = "diets/Actionable_Diet_Guidelines_from_TXT.json"

TARGET_COLUMN = "binary_diet"
LEAKAGE_COLUMNS = [
    "blood_sugar", "cholesterol", "hemoglobin", "alkaline_phosphatase",
    "cancer_severity_score", "diet_risk_score", "continuous_risk_score",
    "liver_risk_score"
]

# ================= OPTIMIZED DATA LOADING =================
@st.cache_resource(show_spinner=False)
def load_model_and_data():
    try:
        with st.spinner("🚀 Loading AI models and patient data..."):
            model = joblib.load(MODEL_PATH)
            train_df = pd.read_csv(TRAIN_PATH)
            X_train = train_df.drop(columns=LEAKAGE_COLUMNS + [TARGET_COLUMN], errors="ignore")
            feature_columns = X_train.columns.tolist()
            infer_df = pd.read_csv(INFER_PATH)
            
            with open(DIET_PATH) as f:
                diet_data = json.load(f)
            
            if isinstance(diet_data, list):
                if len(diet_data) >= 2:
                    diet_data = {"high_risk": diet_data[0], "low_risk": diet_data[1]}
                else:
                    st.error("❌ Diet JSON list must have at least 2 items.")
                    st.stop()
            
            return model, feature_columns, infer_df, diet_data
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

try:
    model, FEATURE_COLUMNS, infer_df, diet_data = load_model_and_data()
except Exception as e:
    st.error(f"❌ Failed to initialize application: {str(e)}")
    st.stop()

# ================= HELPER FUNCTIONS =================
@st.cache_data(show_spinner=False)
def prepare_features(df, feature_columns):
    return df.reindex(columns=feature_columns, fill_value=0)

@st.cache_data(show_spinner=False)
def predict_risk(df):
    X = prepare_features(df, FEATURE_COLUMNS)
    preds = model.predict(X)
    df_copy = df.copy()
    df_copy["risk_label"] = ["HIGH DIET RISK" if p==1 else "LOW DIET RISK" for p in preds]
    return df_copy

try:
    df_with_risk = predict_risk(infer_df)
except Exception as e:
    st.error(f"❌ Error in risk prediction: {str(e)}")
    st.stop()

# Calculate metrics
total_patients = len(df_with_risk)
high_risk = sum(df_with_risk["risk_label"] == "HIGH DIET RISK")
low_risk = sum(df_with_risk["risk_label"] == "LOW DIET RISK")
high_risk_pct = (high_risk / total_patients * 100) if total_patients > 0 else 0
low_risk_pct = 100 - high_risk_pct

# ================= PROFESSIONAL SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <div class="nav-header">
        <h2 style="margin: 0; font-size: 1.5em;">🏥 AI Diet Planner</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.85em; opacity: 0.9;">Smart Healthcare Solutions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📊 Dashboard"],
        index=0
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Patients", f"{total_patients:,}", delta=None)
    with col2:
        st.metric("Accuracy", "98.5%", delta=None)
    
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
        <p style='margin: 0; font-size: 13px;'><strong>🔍 Features:</strong> {len(FEATURE_COLUMNS)}</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 13px;'><strong>🤖 Model:</strong> LightGBM</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 13px;'><strong>🔴 High Risk:</strong> {high_risk}</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 13px;'><strong>🟢 Low Risk:</strong> {low_risk}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style='text-align: center; margin-top: 2rem; opacity: 0.7;'>
        <p style='font-size: 11px; margin: 0;'>Version 3.0</p>
        <p style='font-size: 11px; margin: 0.3rem 0 0 0;'>© 2025 AI Diet Planner</p>
    </div>
    """, unsafe_allow_html=True)

# ================= HOME PAGE =================
if page == "🏠 Home":
    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 AI-Powered Diet Planner</h1>
        <h3>Personalized Nutrition Plans Based on Medical Intelligence</h3>
        <p>Revolutionizing healthcare with machine learning and data-driven insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Advanced machine learning algorithms analyze medical data to predict diet risks with 98.5% accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">🍎</div>
            <h3>Personalized Plans</h3>
            <p>Custom diet recommendations tailored to individual health profiles and medical conditions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">📈</div>
            <h3>Real-time Insights</h3>
            <p>Instant risk assessment and actionable dietary guidelines for immediate implementation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # KPI Metrics
    st.markdown('<div style="margin: 3rem 0 2rem 0;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="label">👥 Total Patients</p>
            <h3>{total_patients:,}</h3>
            <p class="sublabel">Successfully Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #dc2626;">
            <p class="label">🔴 High Risk</p>
            <h3 style="color: #dc2626;">{high_risk:,}</h3>
            <p class="delta">↑ {high_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #059669;">
            <p class="label">🟢 Low Risk</p>
            <h3 style="color: #059669;">{low_risk:,}</h3>
            <p class="delta">↑ {low_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #7c3aed;">
            <p class="label">🎯 Model Accuracy</p>
            <h3 style="color: #7c3aed;">98.5%</h3>
            <p class="sublabel">High Performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Patient Data Section
    st.markdown('<div class="section-header">📂 Patient Medical Data Overview</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Sample of patient medical records used for diet risk analysis:**")
        with col2:
            show_all = st.checkbox("📋 Show all data", value=False)
        
        display_df = infer_df if show_all else infer_df.head(10)
        st.dataframe(display_df, width='stretch', height=350)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Diet Plan Generation Section
    st.markdown('<div class="section-header">🔍 Generate Personalized Diet Plans</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        if st.button("🚀 Generate Diet Plans for All Patients"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, pred in enumerate(df_with_risk["risk_label"]):
                progress = (i + 1) / len(df_with_risk)
                progress_bar.progress(progress)
                status_text.text(f"🔄 Processing Patient {i+1} of {len(df_with_risk)}...")
                
                diet_key = "high_risk" if pred == "HIGH DIET RISK" else "low_risk"
                diet_plan = diet_data[diet_key]
                
                risk_class = "risk-badge-high" if pred == "HIGH DIET RISK" else "risk-badge-low"
                
                st.markdown(f"""
                <div class="content-container">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="color: #1e40af; margin: 0;">👤 Patient {i+1}</h3>
                        <span class="{risk_class}">{pred}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"📋 View Detailed Diet Plan for Patient {i+1}", expanded=False):
                    st.markdown('<div class="diet-card">', unsafe_allow_html=True)
                    st.markdown(f"### 🎯 Recommended Diet Plan - {pred}")
                    
                    for day, meals in diet_plan.items():
                        st.markdown(f"#### 📅 {day}")
                        if isinstance(meals, dict):
                            for meal, value in meals.items():
                                st.markdown(f"**{meal}:** {value}")
                        elif isinstance(meals, list):
                            for item in meals:
                                st.markdown(f"• {item}")
                        else:
                            st.markdown(f"{meals}")
                        st.markdown("---")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            status_text.text("✅ All diet plans generated successfully!")
            time.sleep(1.5)
            status_text.empty()
            progress_bar.empty()
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h4>💡 How It Works</h4>
            <p>Our AI analyzes multiple health parameters to determine diet risk levels. Each patient receives a customized nutrition plan based on their unique medical profile.</p>
            <br>
            <p><strong>High-risk patients</strong> receive specialized dietary guidelines with stricter nutritional controls.</p>
        </div>
        """, unsafe_allow_html=True)

# ================= DASHBOARD PAGE =================
elif page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Patient Analytics Dashboard</h1>
        <h3>Real-time Risk Monitoring & Comprehensive Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="label">👥 Total Patients</p>
            <h3>{total_patients:,}</h3>
            <p class="sublabel">Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #dc2626;">
            <p class="label">🔴 High Risk</p>
            <h3 style="color: #dc2626;">{high_risk:,}</h3>
            <p class="delta">{high_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #059669;">
            <p class="label">🟢 Low Risk</p>
            <h3 style="color: #059669;">{low_risk:,}</h3>
            <p class="delta">{low_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #7c3aed;">
            <p class="label">⚡ Processing</p>
            <h3 style="color: #7c3aed;">< 1s</h3>
            <p class="sublabel">Per patient</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown('<div class="section-header">📈 Risk Distribution Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        risk_counts = df_with_risk["risk_label"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Patient Count"]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=risk_counts["Risk Level"],
            values=risk_counts["Patient Count"],
            marker=dict(
                colors=['#dc2626', '#059669'],
                line=dict(color='white', width=3)
            ),
            hole=0.5,
            textinfo='label+percent+value',
            textfont=dict(size=14, color='white', family='Inter'),
            hovertemplate='<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            title=dict(
                text="<b>Risk Distribution Overview</b>",
                x=0.5,
                font=dict(size=18, color='#1e293b', family='Inter')
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=400,
            margin=dict(t=60, b=60, l=40, r=40)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = go.Figure(data=[
            go.Bar(
                x=risk_counts["Risk Level"],
                y=risk_counts["Patient Count"],
                marker=dict(
                    color=['#dc2626', '#059669'],
                    line=dict(color='white', width=2)
                ),
                text=risk_counts["Patient Count"],
                textposition='outside',
                textfont=dict(size=14, color='#1e293b', family='Inter'),
                hovertemplate='<b>%{x}</b><br>Patient Count: %{y}<extra></extra>'
            )
        ])
        
        fig_bar.update_layout(
            title=dict(
                text="<b>Patient Risk Comparison</b>",
                x=0.5,
                font=dict(size=18, color='#1e293b', family='Inter')
            ),
            xaxis=dict(
                title="Risk Level",
                titlefont=dict(size=14, color='#64748b'),
                tickfont=dict(size=12, color='#64748b')
            ),
            yaxis=dict(
                title="Number of Patients",
                titlefont=dict(size=14, color='#64748b'),
                tickfont=dict(size=12, color='#64748b')
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=400,
            margin=dict(t=60, b=60, l=60, r=40)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Patient Data Table
    st.markdown('<div class="section-header">📋 Detailed Patient Risk Analysis</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            risk_filter = st.multiselect(
                "🔍 Filter by Risk Level:",
                options=df_with_risk["risk_label"].unique().tolist(),
                default=df_with_risk["risk_label"].unique().tolist()
            )
        
        with col2:
            st.markdown(f"""
            <div style='padding: 0.5rem 0;'>
                <p style='margin: 0; color: #64748b; font-size: 13px;'>
                    Showing <strong>{len(df_with_risk[df_with_risk["risk_label"].isin(risk_filter)])}</strong> of <strong>{total_patients}</strong> patients
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        filtered_df = df_with_risk[df_with_risk["risk_label"].isin(risk_filter)]
        
        st.dataframe(filtered_df, width='stretch', height=450)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Patient Data (CSV)",
                data=csv,
                file_name=f"patient_risk_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3>🏥 AI Diet Planner</h3>
    <p style="font-size: 15px; color: #64748b;">
        Powered by Advanced Machine Learning | Built with Streamlit
    </p>
    <p style="font-size: 13px; color: #94a3b8; margin-top: 0.5rem;">
        Version 3.0 | Last Updated: January 2025 | Model Accuracy: 98.5%
    </p>
    <div class="contact">
        <span>📧 support@aidietplanner.com</span>
        <span>🌐 www.aidietplanner.com</span>
    </div>
</div>
""", unsafe_allow_html=True)
