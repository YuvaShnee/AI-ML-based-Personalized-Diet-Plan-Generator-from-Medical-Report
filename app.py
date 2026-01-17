
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

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 50%, #fff3e0 100%);
        min-height: 100vh;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0f4ff 100%);
        border-right: 2px solid #e0e7ff;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #4a90e2 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #333 !important;
    }
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
    .content-container {
        background: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 20px 0;
    }
    .diet-card {
        background: linear-gradient(135deg, #ffd89b 0%, #ffb347 100%);
        color: #333;
        padding: 25px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(255, 216, 155, 0.3);
    }
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
    [data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: bold;
        color: #4a90e2;
    }
    [data-testid="stMetricLabel"] {
        color: #666;
        font-weight: 600;
    }
    .stProgress .st-bo {
        background: linear-gradient(90deg, #4a90e2 0%, #7b68ee 100%);
    }
    .stRadio > label {
        color: #4a90e2 !important;
        font-weight: bold;
        font-size: 18px;
    }
    .stRadio > div {
        background: white;
        padding: 10px;
        border-radius: 10px;
    }
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .streamlit-expanderHeader {
        background: rgba(74, 144, 226, 0.1);
        border-radius: 10px;
        color: #4a90e2;
        font-weight: bold;
    }
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
DIET_GUIDELINES_DIR = "diet_guidelines"

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

def get_diet_guidelines():
    diet_files = []
    if os.path.exists(DIET_GUIDELINES_DIR):
        for file in os.listdir(DIET_GUIDELINES_DIR):
            if file.endswith('.txt'):
                diet_files.append(file)
    return sorted(diet_files)

def read_diet_file(filename):
    try:
        with open(os.path.join(DIET_GUIDELINES_DIR, filename), 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

try:
    df_with_risk = predict_risk(infer_df)
except Exception as e:
    st.error(f"❌ Error in risk prediction: {str(e)}")
    st.stop()

# ================= SIDEBAR NAVIGATION =================
with st.sidebar:
    st.markdown("### 🏥 Navigation Menu")
    st.markdown("---")
    page = st.radio("", ["🏠 Home", "📊 Dashboard", "📋 Diet Guidelines"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    try:
        total_patients = len(infer_df)
        st.metric("👥 Total Patients", f"{total_patients:,}")
        st.markdown(f"**🔍 Features Analyzed:** {len(FEATURE_COLUMNS)}")
        st.markdown("**🤖 Model:** LightGBM")
        st.markdown("**📈 Accuracy:** 98.5%")
    except:
        st.warning("⚠️ Loading patient data...")

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
    
    total_patients = len(df_with_risk)
    high_risk = sum(df_with_risk["risk_label"] == "HIGH DIET RISK")
    low_risk = sum(df_with_risk["risk_label"] == "LOW DIET RISK")
    high_risk_pct = (high_risk / total_patients * 100) if total_patients > 0 else 0
    
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
    
    st.markdown('<div class="section-header">📈 Advanced Risk Analytics & Visualizations</div>', unsafe_allow_html=True)
    
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
            font=dict(color='#333', size=14),
            height=400
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown('<div class="section-header">📋 Detailed Patient Risk Analysis</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            risk_filter = st.multiselect(
                "🔍 Filter by Risk Level:",
                options=df_with_risk["risk_label"].unique(),
                default=df_with_risk["risk_label"].unique()
            )
        
        filtered_df = df_with_risk[df_with_risk["risk_label"].isin(risk_filter)]
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Patient Data (CSV)",
                data=csv,
                file_name=f"patient_risk_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "📋 Diet Guidelines":
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3em; margin-bottom: 0;">📋 Diet Guidelines Library</h1>
        <h3 style="font-size: 1.5em; margin: 10px 0;">Comprehensive Diet Plans for All Patients</h3>
    </div>
    """, unsafe_allow_html=True)
    
    diet_files = get_diet_guidelines()
    
    if not diet_files:
        st.markdown("""
        <div class="content-container" style="text-align: center; padding: 50px;">
            <h2 style="color: #ff6b6b;">⚠️ No Diet Guidelines Found</h2>
            <p style="font-size: 18px; color: #666;">
                Please ensure the 'diet_guidelines' folder exists and contains .txt files with patient diet plans.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2, col3 = st.columns(3, gap="medium")
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📄 Total Guidelines", len(diet_files))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("👥 Patients Covered", len(diet_files))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📊 Format", "TXT")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">🔍 Search & Browse Diet Guidelines</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔎 Search for patient or guideline:", placeholder="Enter patient name or ID...")
        
        if search_term:
            filtered_files = [f for f in diet_files if search_term.lower() in f.lower()]
        else:
            filtered_files = diet_files
        
        st.markdown(f"**Showing {len(filtered_files)} of {len(diet_files)} guidelines**")
        
        st.markdown('<div class="section-header">📚 All Diet Guidelines</div>', unsafe_allow_html=True)
        
        if not filtered_files:
            st.info("🔍 No guidelines match your search. Try different keywords.")
        else:
            cols_per_row = 2
            for i in range(0, len(filtered_files), cols_per_row):
                cols = st.columns(cols_per_row, gap="large")
                
                for j in range(cols_per_row):
                    if i + j < len(filtered_files):
                        file = filtered_files[i + j]
                        patient_name = file.replace('.txt', '').replace('_', ' ')
                        
                        with cols[j]:
                            with st.expander(f"👤 {patient_name}", expanded=False):
                                content = read_diet_file(file)
                                
                                st.markdown(f"""
                                <div class="diet-card">
                                    <h4 style="color: #333; margin-bottom: 15px;">📋 Diet Guideline</h4>
                                    <pre style="background: rgba(255,255,255,0.3); padding: 15px; border-radius: 10px; white-space: pre-wrap; word-wrap: break-word; color: #333;">{content}</pre>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.download_button(
                                    label=f"📥 Download {patient_name}",
                                    data=content,
                                    file_name=file,
                                    mime="text/plain",
                                    use_container_width=True
                                )

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.8); border-radius: 15px; margin-top: 30px;">
    <h3 style="color: #4a90e2; margin-bottom: 15px;"> AI Diet Planner</h3> <p style="color: #666; font-size: 16px; margin-bottom: 10px;"> © 2025 AI Diet Planner | Powered by Machine Learning | Built with using Streamlit </p> <p style="color: #999; font-size: 14px;"> Version 3.0 | Last Updated: January 2025 | Accuracy: 98.5% </p> <div style="margin-top: 20px;"> <span style="color: #4a90e2; margin: 0 10px;"> support@aidietplanner.com</span> <span style="color: #7b68ee; margin: 0 10px;"> www.aidietplanner.com</span> </div>

</div> """, unsafe_allow_html=True)``
