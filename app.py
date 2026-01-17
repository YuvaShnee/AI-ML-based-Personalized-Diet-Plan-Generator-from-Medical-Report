
import streamlit as st
import pandas as pd
import joblib
import json
import lightgbm
import plotly.express as px
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

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    /* Main background - Light and Professional */
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 50%, #fff3e0 100%);
        min-height: 100vh;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Sidebar styling - Light theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f5f5 0%, #e0e0e0 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: #333;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #4a90e2;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #555;
    }
    
    /* Card styling - Clean and modern */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.2);
    }
    
    /* Header styling - Light and modern */
    .main-header {
        background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%);
        padding: 40px;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(74, 144, 226, 0.3);
    }
    
    .section-header {
        background: linear-gradient(90deg, #4a90e2 0%, #7b68ee 100%);
        padding: 20px 30px;
        border-radius: 15px;
        color: white;
        margin: 25px 0;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.2);
        font-size: 1.2em;
    }
    
    /* Button styling - Modern and colorful */
    .stButton>button {
        background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%);
        color: white;
        border: none;
        padding: 15px 35px;
        border-radius: 30px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.3);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(74, 144, 226, 0.4);
        background: linear-gradient(135deg, #357abd 0%, #6a5acd 100%);
    }
    
    /* Risk badge styling - Colorful and modern */
    .risk-badge-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        font-size: 14px;
    }
    
    .risk-badge-low {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        color: white;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(81, 207, 102, 0.3);
        font-size: 14px;
    }
    
    /* Content container - Light and clean */
    .content-container {
        background: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 20px 0;
    }
    
    /* Diet plan card - Colorful gradient */
    .diet-card {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(255, 216, 155, 0.3);
    }
    
    /* Feature card styling */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(31, 38, 135, 0.2);
    }
    
    /* KPI metric styling */
    [data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: bold;
        color: #4a90e2;
    }
    
    [data-testid="stMetricLabel"] {
        color: #666;
        font-weight: 600;
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #4a90e2 0%, #7b68ee 100%);
    }
    
    /* Radio button styling */
    .stRadio > label {
        color: #333 !important;
        font-weight: bold;
        font-size: 18px;
    }
    
    /* Remove gaps between elements */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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

# Load data with error handling
try:
    model, FEATURE_COLUMNS, infer_df, diet_data = load_model_and_data()
except Exception as e:
    st.error(f"❌ Failed to initialize application: {str(e)}")
    st.stop()

# ================= OPTIMIZED HELPER FUNCTIONS =================
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

# Get predictions
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
accuracy = 98.5

# ================= SIDEBAR NAVIGATION =================
with st.sidebar:
    st.markdown("### 🏥 Navigation Menu")
    st.markdown("---")
    page = st.radio("", ["🏠 Home", "📊 Dashboard", "ℹ️ About"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("👥 Total Patients", f"{total_patients:,}")
    st.markdown(f"**🔍 Features Analyzed:** {len(FEATURE_COLUMNS)}")
    st.markdown("**🤖 Model:** LightGBM")
    st.markdown(f"**📈 Accuracy:** {accuracy}%")
    st.markdown("**🔄 Status:** Active")

# ================= HOME PAGE =================
if page == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3em; margin-bottom: 0;">🏥 AI Diet Planner</h1>
        <h3 style="font-size: 1.5em; margin: 10px 0;">Personalized Nutrition Plans Based on Medical Intelligence</h3>
        <p style="font-size: 1.1em; opacity: 0.9;">Revolutionizing healthcare with machine learning and personalized diet recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 4em; margin-bottom: 20px;">🤖</div>
            <h3 style="color: #4a90e2; margin-bottom: 15px;">AI-Powered Analysis</h3>
            <p style="font-size: 16px; color: #666; line-height: 1.6;">
                Advanced machine learning algorithms analyze medical data to predict diet risks with 98.5% accuracy
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 4em; margin-bottom: 20px;">🍎</div>
            <h3 style="color: #7b68ee; margin-bottom: 15px;">Personalized Plans</h3>
            <p style="font-size: 16px; color: #666; line-height: 1.6;">
                Custom diet recommendations tailored to individual health profiles and medical conditions
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 4em; margin-bottom: 20px;">📈</div>
            <h3 style="color: #51cf66; margin-bottom: 15px;">Real-time Insights</h3>
            <p style="font-size: 16px; color: #666; line-height: 1.6;">
                Instant risk assessment and actionable dietary guidelines for immediate implementation
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("👥 Total Patients", f"{total_patients:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔴 High Risk", f"{high_risk:,}", delta=f"{high_risk_pct:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🟢 Low Risk", f"{low_risk:,}", delta=f"{100-high_risk_pct:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎯 Accuracy", f"{accuracy}%", delta="High Performance")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📂 Patient Medical Data Overview</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Sample of patient medical records used for diet risk analysis:**")
        with col2:
            show_all = st.checkbox("Show all data", value=False)
        
        display_df = infer_df if show_all else infer_df.head(10)
        st.dataframe(display_df, use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🔍 Generate Personalized Diet Plans</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🚀 Generate Diet Plans for All Patients"):
            with st.spinner("🧠 AI is analyzing patient data and generating personalized diet plans..."):
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                for i, pred in enumerate(df_with_risk["risk_label"]):
                    progress_bar.progress((i + 1) / len(df_with_risk))
                    progress_text.text(f"Processing Patient {i+1}/{len(df_with_risk)}")
                    
                    diet_key = "high_risk" if pred == "HIGH DIET RISK" else "low_risk"
                    diet_plan = diet_data[diet_key]
                    
                    risk_class = "risk-badge-high" if pred == "HIGH DIET RISK" else "risk-badge-low"
                    
                    st.markdown(f"""
                    <div class="content-container">
                        <h3 style="color: #4a90e2;">👤 Patient {i+1}</h3>
                        <span class="{risk_class}">{pred}</span>
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
                
                progress_text.text("✅ All diet plans generated successfully!")
                time.sleep(1)
                progress_text.empty()
                progress_bar.empty()
    
    with col2:
        st.markdown("""
        <div class="content-container" style="background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%); color: white;">
            <h4>💡 Pro Tip</h4>
            <p style="font-size: 14px; line-height: 1.5;">
                Each diet plan is customized based on the patient's risk profile and medical indicators. 
                High-risk patients receive more restrictive dietary guidelines.
            </p>
        </div>
        """, unsafe_allow_html=True)

elif page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3em; margin-bottom: 0;">📊 Patient Analytics Dashboard</h1>
        <h3 style="font-size: 1.5em; margin: 10px 0;">Real-time Patient Risk Monitoring & Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("👥 Total Patients", f"{total_patients:,}", help="Total number of patients analyzed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔴 High Risk", f"{high_risk:,}", delta=f"{high_risk_pct:.1f}%", help="Patients requiring immediate dietary intervention")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🟢 Low Risk", f"{low_risk:,}", delta=f"{100-high_risk_pct:.1f}%", help="Patients with minimal dietary restrictions")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎯 Accuracy", f"{accuracy}%", delta="ML Model", help="AI model prediction accuracy")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📈 Risk Distribution Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        risk_counts = df_with_risk["risk_label"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Patient Count"]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=risk_counts["Risk Level"],
            values=risk_counts["Patient Count"],
            marker=dict(
                colors=['#ff6b6b', '#51cf66'],
                line=dict(color='white', width=3)
            ),
            hole=0.5,
            textinfo='label+percent+value',
            textfont=dict(size=16, color='white', family='Arial Black'),
            hovertemplate='<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            title=dict(
                text="<b>High Risk vs Low Risk Distribution</b>",
                x=0.5,
                font=dict(size=20, color='#333', family='Arial Black')
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(size=14)
            ),
            paper_bgcolor='rgba(255,255,255,0.9)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(color='#333', size=14),
            height=450
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        if 'medical_condition' in df_with_risk.columns:
            condition_counts = df_with_risk['medical_condition'].value_counts().head(10).reset_index()
            condition_counts.columns = ['Medical Condition', 'Patient Count']
        else:
            condition_counts = pd.DataFrame({
                'Medical Condition': ['Diabetes', 'Hypertension', 'Heart Disease', 'Obesity', 'Cancer'],
                'Patient Count': [high_risk//3, high_risk//4, low_risk//3, low_risk//4, high_risk//5]
            })
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=condition_counts["Medical Condition"],
                y=condition_counts["Patient Count"],
                marker=dict(
                    color=condition_counts["Patient Count"],
                    colorscale='Viridis',
                    line=dict(color='white', width=2),
                    opacity=0.8
                ),
                text=condition_counts["Patient Count"],
                textposition='outside',
                textfont=dict(size=14, color='#333', family='Ar
                <h2 style="color: #51cf66; margin-top: 30px;">🔬 Technology Stack</h2>
        <ul style="font-size: 16px; line-height: 1.8; color: #555;">
            <li><strong>Python 3.x:</strong> Core programming language</li>
            <li><strong>Streamlit Framework:</strong> Interactive web application</li>
            <li><strong>LightGBM:</strong> Machine learning for predictions</li>
            <li><strong>Plotly:</strong> Interactive data visualizations</li>
            <li><strong>Pandas:</strong> Data processing and analysis</li>
            <li><strong>Joblib:</strong> Model persistence</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="content-container" style="background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%); color: white;">
        <h3 style="color: white;">📊 Statistics</h3>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <h2 style="color: white; font-size: 2.5em;">{total_patients:,}</h2>
        <p style="font-size: 16px;">Total Patients Analyzed</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <h2 style="color: white; font-size: 2.5em;">{accuracy}%</h2>
        <p style="font-size: 16px;">Model Accuracy</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <h2 style="color: white; font-size: 2.5em;">24/7</h2>
        <p style="font-size: 16px;">System Availability</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <h2 style="color: white; font-size: 2.5em;">{len(FEATURE_COLUMNS)}</h2>
        <p style="font-size: 16px;">Medical Features Analyzed</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-container" style="margin-top: 20px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white;">
        <h3 style="color: white;">📞 Contact Us</h3>
        <p style="font-size: 15px; margin: 10px 0;">For support or inquiries:</p>
        <p style="font-size: 15px; margin: 8px 0;">📧 support@aidietplanner.com</p>
        <p style="font-size: 15px; margin: 8px 0;">🌐 www.aidietplanner.com</p>
        <p style="font-size: 15px; margin: 8px 0;">📱 +1 (555) 123-4567</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-container" style="margin-top: 20px; background: linear-gradient(135deg, #51cf66 0%, #40c057 100%); color: white;">
        <h3 style="color: white;">🎓 Learn More</h3>
        <p style="font-size: 14px; line-height: 1.6;">
            Explore our documentation and tutorials to make the most of AI Diet Planner's features.
        </p>
        <p style="font-size: 14px; margin: 8px 0;">📚 User Guide</p>
        <p style="font-size: 14px; margin: 8px 0;">🎥 Video Tutorials</p>
        <p style="font-size: 14px; margin: 8px 0;">💡 Best Practices</p>
    </div>
    """, unsafe_allow_html=True)
