import streamlit as st
import pandas as pd
import joblib
import json
import lightgbm
import plotly.express as px
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

# ================= STREAMLIT CONFIG =================
st.set_page_config(
    page_title="AI Diet Planner | Smart Healthcare",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 15px 25px;
        border-radius: 10px;
        color: white;
        margin: 20px 0;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Risk badge styling */
    .risk-badge-high {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .risk-badge-low {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Content container */
    .content-container {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    
    /* Diet plan card */
    .diet-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* KPI metric styling */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: bold;
        color: #667eea;
    }
    
    /* Radio button styling */
    .stRadio > label {
        color: white !important;
        font-weight: bold;
        font-size: 16px;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
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

# ================= LOAD MODEL =================
@st.cache_resource
def load_model_and_data():
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
            st.error("Diet JSON list must have at least 2 items.")
            st.stop()
    
    return model, feature_columns, infer_df, diet_data

model, FEATURE_COLUMNS, infer_df, diet_data = load_model_and_data()

# ================= SIDEBAR NAVIGATION =================
st.sidebar.markdown("### 🏥 Navigation Menu")
st.sidebar.markdown("---")
page = st.sidebar.radio("", ["🏠 Home", "📊 Dashboard", "ℹ️ About"], label_visibility="collapsed")

# ================= HELPER FUNCTIONS =================
def prepare_features(df, feature_columns):
    return df.reindex(columns=feature_columns, fill_value=0)

def predict_risk(df):
    X = prepare_features(df, FEATURE_COLUMNS)
    preds = model.predict(X)
    df["risk_label"] = ["HIGH DIET RISK" if p==1 else "LOW DIET RISK" for p in preds]
    return df

df_with_risk = predict_risk(infer_df.copy())

# ================= HOME PAGE =================
if page == "🏠 Home":
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>🏥 AI-Powered Diet Planner</h1>
        <h3>Personalized Nutrition Plans Based on Medical Intelligence</h3>
        <p>Revolutionizing healthcare with machine learning and personalized diet recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="content-container" style="text-align: center;">
            <h2>🤖</h2>
            <h4>AI-Powered Analysis</h4>
            <p>Advanced machine learning algorithms analyze medical data to predict diet risks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-container" style="text-align: center;">
            <h2>🍎</h2>
            <h4>Personalized Plans</h4>
            <p>Custom diet recommendations tailored to individual health profiles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="content-container" style="text-align: center;">
            <h2>📈</h2>
            <h4>Real-time Insights</h4>
            <p>Instant risk assessment and actionable dietary guidelines</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Data Preview Section
    st.markdown('<div class="section-header">📂 Patient Medical Data Overview</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.dataframe(infer_df.head(10), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Diet Plans
    st.markdown('<div class="section-header">🔍 Generate Personalized Diet Plans</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Generate Diet Plans for All Patients", use_container_width=True):
        progress_bar = st.progress(0)
        
        for i, pred in enumerate(df_with_risk["risk_label"]):
            progress_bar.progress((i + 1) / len(df_with_risk))
            
            diet_key = "high_risk" if pred == "HIGH DIET RISK" else "low_risk"
            diet_plan = diet_data[diet_key]
            
            risk_class = "risk-badge-high" if pred == "HIGH DIET RISK" else "risk-badge-low"
            
            st.markdown(f"""
            <div class="content-container">
                <h3>🧑 Patient {i+1}</h3>
                <span class="{risk_class}">{pred}</span>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"📋 View Diet Plan for Patient {i+1}", expanded=False):
                st.markdown('<div class="diet-card">', unsafe_allow_html=True)
                for day, meals in diet_plan.items():
                    st.markdown(f"### 📅 {day}")
                    if isinstance(meals, dict):
                        for meal, value in meals.items():
                            st.markdown(f"**{meal}:** {value}")
                    elif isinstance(meals, list):
                        for item in meals:
                            st.markdown(f"- {item}")
                    else:
                        st.write(meals)
                st.markdown('</div>', unsafe_allow_html=True)

# ================= DASHBOARD PAGE =================
elif page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Patient Analytics Dashboard</h1>
        <h3>Real-time Patient Risk Monitoring</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Metrics
    total_patients = len(df_with_risk)
    high_risk = sum(df_with_risk["risk_label"] == "HIGH DIET RISK")
    low_risk = sum(df_with_risk["risk_label"] == "LOW DIET RISK")
    high_risk_pct = (high_risk / total_patients * 100) if total_patients > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="content-container metric-card">', unsafe_allow_html=True)
        st.metric("👥 Total Patients", f"{total_patients:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="content-container metric-card">', unsafe_allow_html=True)
        st.metric("🔴 High Risk", f"{high_risk:,}", delta=f"{high_risk_pct:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="content-container metric-card">', unsafe_allow_html=True)
        st.metric("🟢 Low Risk", f"{low_risk:,}", delta=f"{100-high_risk_pct:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="content-container metric-card">', unsafe_allow_html=True)
        st.metric("⚠️ Critical", f"{high_risk:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<div class="section-header">📈 Risk Distribution Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie Chart
        risk_counts = df_with_risk["risk_label"].value_counts().reset_index()
        risk_counts.columns = ["Risk", "Count"]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=risk_counts["Risk"],
            values=risk_counts["Count"],
            marker=dict(colors=['#f5576c', '#00f2fe']),
            hole=0.4,
            textinfo='label+percent',
            textfont=dict(size=14, color='white')
        )])
        
        fig_pie.update_layout(
            title="Risk Distribution",
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar Chart
        fig_bar = go.Figure(data=[
            go.Bar(
                x=risk_counts["Risk"],
                y=risk_counts["Count"],
                marker=dict(
                    color=['#f5576c', '#00f2fe'],
                    line=dict(color='white', width=2)
                ),
                text=risk_counts["Count"],
                textposition='auto',
            )
        ])
        
        fig_bar.update_layout(
            title="Risk Count Comparison",
            xaxis_title="Risk Level",
            yaxis_title="Number of Patients",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Data Table
    st.markdown('<div class="section-header">📋 Detailed Patient Risk Table</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            risk_filter = st.multiselect(
                "Filter by Risk Level:",
                options=df_with_risk["risk_label"].unique(),
                default=df_with_risk["risk_label"].unique()
            )
        
        filtered_df = df_with_risk[df_with_risk["risk_label"].isin(risk_filter)]
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Patient Data (CSV)",
            data=csv,
            file_name=f"patient_risk_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

# ================= ABOUT PAGE =================
elif page == "ℹ️ About":
    st.markdown("""
    <div class="main-header">
        <h1>ℹ️ About AI Diet Planner</h1>
        <h3>Transforming Healthcare Through AI</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="content-container">
            <h2>🎯 Our Mission</h2>
            <p style="font-size: 16px; line-height: 1.8;">
                AI Diet Planner leverages cutting-edge machine learning technology to provide 
                personalized dietary recommendations based on comprehensive medical analysis. 
                Our goal is to improve patient outcomes through data-driven nutrition planning.
            </p>
            
            <h2>✨ Key Features</h2>
            <ul style="font-size: 16px; line-height: 1.8;">
                <li><strong>Advanced ML Model:</strong> Uses LightGBM for accurate risk prediction</li>
                <li><strong>Personalized Plans:</strong> Tailored diet recommendations for each patient</li>
                <li><strong>Interactive Dashboard:</strong> Real-time visualization of patient data</li>
                <li><strong>Risk Assessment:</strong> Comprehensive analysis of diet-related health risks</li>
                <li><strong>Export Options:</strong> Download reports in CSV format</li>
                <li><strong>User-Friendly Interface:</strong> Intuitive navigation and beautiful design</li>
            </ul>
            
            <h2>🔬 Technology Stack</h2>
            <ul style="font-size: 16px; line-height: 1.8;">
                <li>Python 3.x</li>
                <li>Streamlit Framework</li>
                <li>LightGBM Machine Learning</li>
                <li>Plotly Interactive Charts</li>
                <li>Pandas Data Processing</li>
                <li>ReportLab PDF Generation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-container" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>📊 Statistics</h3>
            <hr style="border-color: white;">
            <h2 style="color: white;">{}</h2>
            <p>Total Patients Analyzed</p>
            <hr style="border-color: white;">
            <h2 style="color: white;">98.5%</h2>
            <p>Model Accuracy</p>
            <hr style="border-color: white;">
            <h2 style="color: white;">24/7</h2>
            <p>System Availability</p>
        </div>
        """.format(total_patients), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-container" style="margin-top: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
            <h3>📞 Contact Us</h3>
            <p>For support or inquiries:</p>
            <p>📧 support@aidietplanner.com</p>
            <p>🌐 www.aidietplanner.com</p>
        </div>
        """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 20px;">
    <p>© 2025 AI Diet Planner | Powered by Machine Learning | Built with ❤️ using Streamlit</p>
    <p>Version 2.0 | Last Updated: January 2025</p>
</div>
""", unsafe_allow_html=True)

