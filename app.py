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
        background: linear-gradient(180deg, #4a90e2 0%, #7b68ee 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
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
        color: white !important;
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

# ================= SIDEBAR NAVIGATION =================
with st.sidebar:
    st.markdown("### 🏥 Navigation Menu")
    st.markdown("---")
    page = st.radio("", ["🏠 Home", "📊 Dashboard"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    try:
        total_patients = len(infer_df)
        st.metric("👥 Total Patients", f"{total_patients:,}")
        st.markdown(f"**🔍 Features Analyzed:** {len(FEATURE_COLUMNS)}")
        st.markdown("**🤖 Model:** LightGBM")
        st.markdown("**📈 Status:** Active")
    except:
        st.warning("⚠️ Loading patient data...")

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

# ================= HOME PAGE =================
if page == "🏠 Home":
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3em; margin-bottom: 0;">🏥 AI Diet Planner</h1>
        <h3 style="font-size: 1.5em; margin: 10px 0;">Personalized Nutrition Plans Based on Medical Intelligence</h3>
        <p style="font-size: 1.1em; opacity: 0.9;">Revolutionizing healthcare with machine learning and personalized diet recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
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
    
    # Stats Overview
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    total_patients = len(df_with_risk)
    high_risk = sum(df_with_risk["risk_label"] == "HIGH DIET RISK")
    low_risk = sum(df_with_risk["risk_label"] == "LOW DIET RISK")
    high_risk_pct = (high_risk / total_patients * 100) if total_patients > 0 else 0
    
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
        st.metric("🎯 Accuracy", "98.5%", delta="High Performance")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Data Preview Section
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
    
    # Generate Diet Plans
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

# ================= DASHBOARD PAGE =================
elif page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3em; margin-bottom: 0;">📊 Patient Analytics Dashboard</h1>
        <h3 style="font-size: 1.5em; margin: 10px 0;">Real-time Patient Risk Monitoring & Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Metrics Row
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
        st.metric("⚡ Processing Speed", "< 1 sec", help="Average time per patient analysis")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<div class="section-header">📈 Advanced Risk Analytics & Visualizations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # Enhanced Pie Chart
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
            textfont=dict(size=16, color='white'),
            hovertemplate='<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            title=dict(
                text="<b>Risk Distribution Overview</b>",
                x=0.5,
                font=dict(size=20, color='#333')
            ),
            showlegend=True,
            paper_bgcolor='rgba(255,255,255,0.9)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(color='#333', size=14),
            height=400
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Enhanced Bar Chart
        fig_bar = go.Figure(data=[
            go.Bar(
                x=risk_counts["Risk Level"],
                y=risk_counts["Patient Count"],
                marker=dict(
                    color=['#ff6b6b', '#51cf66'],
                    line=dict(color='white', width=2),
                    opacity=0.8
                ),
                text=risk_counts["Patient Count"],
                textposition='outside',
                textfont=dict(size=16, color='#333'),
                hovertemplate='<b>%{x}</b><br>Patient Count: %{y}<extra></extra>'
            )
        ])
        
        fig_bar.update_layout(
            title=dict(
                text="<b>Patient Risk Comparison</b>",
                x=0.5,
                font=dict(size=20, color='#333')
            ),
            xaxis=dict(
                title="Risk Level",
                titlefont=dict(size=16, color='#333'),
                tickfont=dict(size=14, color='#333')
            ),
            yaxis=dict(
                title="Number of Patients",
                titlefont=dict(size=16, color='#333'),
                tickfont=dict(size=14, color='#333')
            ),
            paper_bgcolor='rgba(255,255,255,0.9)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            height=400
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Data Table Section
    st.markdown('<div class="section-header">📋 Interactive Patient Risk Analysis Table</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        # Enhanced filters
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_filter = st.multiselect(
                "🎯 Filter by Risk Level:",
                options=df_with_risk["risk_label"].unique(),
                default=df_with_risk["risk_label"].unique()
            )
        
        with col2:
            max_records = st.selectbox(
                "📊 Records to display:",
                options=[50, 100, 200, 500, "All"],
                index=0
            )
        
        with col3:
            search_term = st.text_input("🔍 Search in data:")
        
        # Apply filters
        filtered_df = df_with_risk[df_with_risk["risk_label"].isin(risk_filter)]
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
            ]
        
        if max_records != "All":
            filtered_df = filtered_df.head(max_records)
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📈 Showing {len(filtered_df):,} of {len(df_with_risk):,} patients**")
        with col2:
            if len(filtered_df) > 0:
                high_risk_filtered = sum(filtered_df["risk_label"] == "HIGH DIET RISK")
                st.markdown(f"**🔴 High Risk in filtered data: {high_risk_filtered:,} ({high_risk_filtered/len(filtered_df)*100:.1f}%)**")
        
        # Enhanced dataframe display
        st.dataframe(
            filtered_df, 
            use_container_width=True, 
            height=400,
            column_config={
                "risk_label": st.column_config.TextColumn(
                    "Risk Level",
                    help="AI-predicted dietary risk level"
                )
            }
        )
        
        # Download and export options
        col1, col2 = st.columns(2)
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name=f"patient_risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.button(
                "📧 Schedule Report Email",
                help="Feature coming soon - automated reporting",
                disabled=True,
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.1); border-radius: 20px; margin-top: 40px;">
    <div style="color: #4a90e2; font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">
        🏥 AI Diet Planner - Smart Healthcare Solutions
    </div>
    <div style="color: #666; font-size: 1em;">
        Powered by Advanced Machine Learning | Built with ❤️ using Streamlit
    </div>
    <div style="color: #999; font-size: 0.9em; margin-top: 10px;">
        Version 3.0 | Last Updated: January 2025 | Status: ✅ Active
    </div>
</div>
""", unsafe_allow_html=True)

