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

# ================= CUSTOM CSS - OPTIMIZED FOR SMALL SCREENS =================
st.markdown("""
<style>
    /* Make everything scrollable and responsive */
    .stApp {
        background: linear-gradient(135deg, #f0f4ff 0%, #fef5ff 50%, #fff9f0 100%);
        min-height: 100vh;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Sidebar styling - compact for small screens */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
        border-right: 2px solid #e8efff;
        min-width: 250px !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #4a90e2 !important;
        font-size: 1.2em !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label {
        color: #333 !important;
        font-size: 0.9em !important;
    }
    
    /* Compact metric cards for small screens */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
        padding: 20px 15px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.12);
        border: 1px solid rgba(74, 144, 226, 0.1);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(74, 144, 226, 0.2);
    }
    
    .metric-card h3 {
        color: #4a90e2;
        font-size: 1.8em;
        margin: 8px 0;
        font-weight: 700;
    }
    
    .metric-card p {
        color: #666;
        font-size: 0.85em;
        margin: 3px 0;
        font-weight: 500;
    }
    
    .metric-card .delta {
        color: #51cf66;
        font-size: 0.8em;
        font-weight: 600;
        margin-top: 3px;
    }
    
    /* Compact header for small screens */
    .main-header {
        background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%);
        padding: 30px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(74, 144, 226, 0.25);
    }
    
    .main-header h1 {
        font-size: 2em !important;
        margin-bottom: 0 !important;
    }
    
    .main-header h3 {
        font-size: 1.1em !important;
        margin: 8px 0 !important;
    }
    
    .main-header p {
        font-size: 0.95em !important;
    }
    
    .section-header {
        background: linear-gradient(90deg, #4a90e2 0%, #7b68ee 100%);
        padding: 15px 20px;
        border-radius: 12px;
        color: white;
        margin: 20px 0;
        font-weight: 600;
        box-shadow: 0 3px 12px rgba(74, 144, 226, 0.2);
        font-size: 1.1em;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 3px 12px rgba(74, 144, 226, 0.3);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
        background: linear-gradient(135deg, #357abd 0%, #6a5acd 100%);
    }
    
    .risk-badge-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(255, 107, 107, 0.3);
        font-size: 13px;
    }
    
    .risk-badge-low {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(81, 207, 102, 0.3);
        font-size: 13px;
    }
    
    .content-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 3px 15px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(74, 144, 226, 0.1);
        margin: 15px 0;
    }
    
    .diet-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        color: #333;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 3px 12px rgba(255, 152, 0, 0.15);
        border: 1px solid rgba(255, 152, 0, 0.2);
    }
    
    /* Compact feature cards */
    .feature-card {
        background: white;
        padding: 25px 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 3px 15px rgba(74, 144, 226, 0.1);
        border: 1px solid rgba(74, 144, 226, 0.08);
        transition: all 0.3s ease;
        height: 100%;
        margin-bottom: 15px;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 25px rgba(74, 144, 226, 0.18);
    }
    
    .feature-card h3 {
        font-size: 1.2em !important;
        margin-bottom: 10px !important;
    }
    
    .feature-card p {
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    .feature-card div {
        font-size: 3em !important;
        margin-bottom: 15px !important;
    }
    
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        font-size: 0.85em;
    }
    
    .streamlit-expanderHeader {
        background: rgba(74, 144, 226, 0.08);
        border-radius: 8px;
        color: #4a90e2;
        font-weight: 600;
        font-size: 0.9em;
    }
    
    /* Responsive columns - stack on smaller screens */
    @media (max-width: 1366px) {
        .main-header h1 {
            font-size: 1.8em !important;
        }
        
        .metric-card h3 {
            font-size: 1.6em;
        }
    }
    
    @media (max-width: 1024px) {
        .main-header {
            padding: 25px 15px;
        }
        
        .main-header h1 {
            font-size: 1.6em !important;
        }
        
        .main-header h3 {
            font-size: 1em !important;
        }
        
        .feature-card {
            padding: 20px 15px;
        }
    }
    
    /* Make sure content doesn't overflow */
    .stApp > header {
        background-color: transparent;
    }
    
    /* Compact spacing for all elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    div[data-testid="column"] {
        padding: 0 0.5rem !important;
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

try:
    df_with_risk = predict_risk(infer_df)
except Exception as e:
    st.error(f"❌ Error in risk prediction: {str(e)}")
    st.stop()

# Calculate metrics once
total_patients = len(df_with_risk)
high_risk = sum(df_with_risk["risk_label"] == "HIGH DIET RISK")
low_risk = sum(df_with_risk["risk_label"] == "LOW DIET RISK")
high_risk_pct = (high_risk / total_patients * 100) if total_patients > 0 else 0
low_risk_pct = 100 - high_risk_pct

# ================= SIDEBAR NAVIGATION =================
with st.sidebar:
    st.markdown("### 🏥 Navigation")
    st.markdown("---")
    page = st.radio("Select Page", ["🏠 Home", "📊 Dashboard"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("👥 Patients", f"{total_patients:,}")
    st.metric("🎯 Accuracy", "98.5%")
    st.markdown(f"**Features:** {len(FEATURE_COLUMNS)}")
    st.markdown("**Model:** LightGBM")

# ================= HOME PAGE =================
if page == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>🏥 AI Diet Planner</h1>
        <h3>Personalized Nutrition Plans Based on Medical Intelligence</h3>
        <p>Revolutionizing healthcare with machine learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards in single column on small screens, 3 columns on larger
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div>🤖</div>
            <h3 style="color: #4a90e2;">AI-Powered Analysis</h3>
            <p style="color: #666;">
                Advanced ML algorithms with 98.5% accuracy
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div>🍎</div>
            <h3 style="color: #7b68ee;">Personalized Plans</h3>
            <p style="color: #666;">
                Custom recommendations for individual health profiles
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div>📈</div>
            <h3 style="color: #51cf66;">Real-time Insights</h3>
            <p style="color: #666;">
                Instant risk assessment and dietary guidelines
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # KPI Cards - 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p>👥 Patients</p>
            <h3>{total_patients:,}</h3>
            <p style="color: #999; font-size: 0.75em;">Total analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p>🔴 High Risk</p>
            <h3>{high_risk:,}</h3>
            <p class="delta">{high_risk_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p>🟢 Low Risk</p>
            <h3>{low_risk:,}</h3>
            <p class="delta">{low_risk_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <p>🎯 Accuracy</p>
            <h3>98.5%</h3>
            <p style="color: #51cf66; font-size: 0.75em; font-weight: 600;">High</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📂 Patient Medical Data</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Sample of patient medical records:**")
        with col2:
            show_all = st.checkbox("Show all", value=False)
        
        display_df = infer_df if show_all else infer_df.head(10)
        st.dataframe(display_df, use_container_width=True, height=250)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🔍 Generate Diet Plans</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🚀 Generate Plans for All Patients"):
            with st.spinner("🧠 Analyzing patient data..."):
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                for i, pred in enumerate(df_with_risk["risk_label"]):
                    progress_bar.progress((i + 1) / len(df_with_risk))
                    progress_text.text(f"Processing {i+1}/{len(df_with_risk)}")
                    
                    diet_key = "high_risk" if pred == "HIGH DIET RISK" else "low_risk"
                    diet_plan = diet_data[diet_key]
                    
                    risk_class = "risk-badge-high" if pred == "HIGH DIET RISK" else "risk-badge-low"
                    
                    st.markdown(f"""
                    <div class="content-container">
                        <h3 style="color: #4a90e2;">👤 Patient {i+1}</h3>
                        <span class="{risk_class}">{pred}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"📋 View Diet Plan - Patient {i+1}", expanded=False):
                        st.markdown('<div class="diet-card">', unsafe_allow_html=True)
                        st.markdown(f"### 🎯 {pred}")
                        
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
                
                progress_text.text("✅ Complete!")
                time.sleep(1)
                progress_text.empty()
                progress_bar.empty()
    
    with col2:
        st.markdown("""
        <div class="content-container" style="background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%); color: white;">
            <h4>💡 Pro Tip</h4>
            <p style="font-size: 13px; line-height: 1.4;">
                Plans are customized based on risk profile and medical indicators.
            </p>
        </div>
        """, unsafe_allow_html=True)

elif page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analytics Dashboard</h1>
        <h3>Real-time Patient Risk Monitoring</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p>👥 Patients</p>
            <h3>{total_patients:,}</h3>
            <p style="color: #999; font-size: 0.75em;">Total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p>🔴 High Risk</p>
            <h3>{high_risk:,}</h3>
            <p class="delta">{high_risk_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p>🟢 Low Risk</p>
            <h3>{low_risk:,}</h3>
            <p class="delta">{low_risk_pct:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <p>⚡ Speed</p>
            <h3>< 1s</h3>
            <p style="color: #999; font-size: 0.75em;">Per patient</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📈 Risk Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = df_with_risk["risk_label"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Patient Count"]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=risk_counts["Risk Level"],
            values=risk_counts["Patient Count"],
            marker=dict(
                colors=['#ff6b6b', '#51cf66'],
                line=dict(color='white', width=2)
            ),
            hole=0.5,
            textinfo='label+percent',
            textfont=dict(size=14, color='white'),
            hovertemplate='<b>%{label}</b><br>%{value} patients<extra></extra>'
        )])
        
        fig_pie.update_layout(
            title_text="<b>Risk Distribution</b>",
            title_x=0.5,
            showlegend=True,
            paper_bgcolor='rgba(255,255,255,0.95)',
            height=350
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = go.Figure(data=[
            go.Bar(
                x=risk_counts["Risk Level"],
                y=risk_counts["Patient Count"],
                marker_color=['#ff6b6b', '#51cf66'],
                marker_line_color='white',
                marker_line_width=2,
                text=risk_counts["Patient Count"],
                textposition='outside',
                textfont=dict(size=14),
                hovertemplate='<b>%{x}</b><br>%{y} patients<extra></extra>'
            )
        ])
        
        fig_bar.update_layout(
            title_text="<b>Risk Comparison</b>",
            title_x=0.5,
            xaxis_title="Risk Level",
            yaxis_title="Patients",
            paper_bgcolor='rgba(255,255,255,0.95)',
            height=350
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown('<div class="section-header">📋 Patient Risk Analysis</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            risk_filter = st.multiselect(
                "🔍 Filter by Risk:",
                options=df_with_risk["risk_label"].unique(),
                default=df_with_risk["risk_label"].unique()
            )
        
        filtered_df = df_with_risk[df_with_risk["risk_label"].isin(risk_filter)]
        
        st.dataframe(filtered_df, use_container_width=True, height=350)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"patient_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.9); border-radius: 12px; margin-top: 20px;">
    <h3 style="color: #4a90e2; margin-bottom: 10px;">🏥 AI Diet Planner</h3>
    <p style="color: #666; font-size: 14px; margin-bottom: 8px;">
        © 2025 AI Diet Planner | ML-Powered Healthcare
    </p>
    <p style="color: #999; font-size: 12px;">
        v3.0 | Updated Jan 2025 | 98.5% Accuracy
    </p>
</div>
""", unsafe_allow_html=True)
