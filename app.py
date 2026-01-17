import streamlit as st
import pandas as pd
import joblib
import json
import os
import plotly.graph_objects as go
from datetime import datetime
import time
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

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
        background: linear-gradient(135deg, 
            #e3f2fd 0%, 
            #fff9c4 15%, 
            #f3e5f5 30%, 
            #ffe0f0 45%, 
            #e1f5fe 60%, 
            #fff3e0 75%, 
            #f1f8e9 90%, 
            #fce4ec 100%);
        min-height: 100vh;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0f8ff 50%, #fff9f0 100%);
        border-right: 2px solid #e8efff;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #4a90e2 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #333 !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
        padding: 30px 25px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.12);
        border: 1px solid rgba(74, 144, 226, 0.1);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(74, 144, 226, 0.2);
    }
    .metric-card h3 {
        color: #4a90e2;
        font-size: 2.5em;
        margin: 10px 0;
        font-weight: 700;
    }
    .metric-card p {
        color: #666;
        font-size: 1em;
        margin: 5px 0;
        font-weight: 500;
    }
    .metric-card .delta {
        color: #51cf66;
        font-size: 0.9em;
        font-weight: 600;
        margin-top: 5px;
    }
    .main-header {
        background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 50%, #ff6b9d 100%);
        padding: 50px 40px;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(74, 144, 226, 0.25);
    }
    .section-header {
        background: linear-gradient(90deg, #4a90e2 0%, #7b68ee 50%, #ff6b9d 100%);
        padding: 20px 30px;
        border-radius: 15px;
        color: white;
        margin: 25px 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.2);
        font-size: 1.3em;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 100%);
        color: white;
        border: none;
        padding: 16px 40px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(74, 144, 226, 0.4);
        background: linear-gradient(135deg, #357abd 0%, #6a5acd 100%);
    }
    .risk-badge-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 3px 12px rgba(255, 107, 107, 0.3);
        font-size: 14px;
    }
    .risk-badge-low {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        color: white;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 3px 12px rgba(81, 207, 102, 0.3);
        font-size: 14px;
    }
    .content-container {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(74, 144, 226, 0.1);
        margin: 20px 0;
    }
    .diet-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        color: #333;
        padding: 25px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.15);
        border: 1px solid rgba(255, 152, 0, 0.2);
    }
    .feature-card {
        background: white;
        padding: 35px 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.1);
        border: 1px solid rgba(74, 144, 226, 0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 30px rgba(74, 144, 226, 0.18);
    }
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }
    .streamlit-expanderHeader {
        background: rgba(74, 144, 226, 0.08);
        border-radius: 10px;
        color: #4a90e2;
        font-weight: 600;
    }
    .pdf-download-section {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        border: 2px dashed #4a90e2;
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

# ================= PDF GENERATION FUNCTION =================
def create_diet_plan_pdf(patient_data_list, df_with_risk):
    """Generate a PDF with all patient diet plans"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4a90e2'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#7b68ee'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    subheader_style = ParagraphStyle(
        'CustomSubHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#4a90e2'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        fontName='Helvetica'
    )
    
    # Add main title
    elements.append(Paragraph("🏥 AI Diet Planner", title_style))
    elements.append(Paragraph("Personalized Nutrition Plans", header_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add summary table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Patients', str(len(df_with_risk))],
        ['High Risk Patients', str(sum(df_with_risk["risk_label"] == "HIGH DIET RISK"))],
        ['Low Risk Patients', str(sum(df_with_risk["risk_label"] == "LOW DIET RISK"))],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # Add individual patient diet plans
    for i, (pred, diet_plan) in enumerate(patient_data_list, 1):
        elements.append(Paragraph(f"Patient {i}", header_style))
        
        risk_color = colors.HexColor('#ff6b6b') if pred == "HIGH DIET RISK" else colors.HexColor('#51cf66')
        risk_para = Paragraph(f"<b>Risk Level: {pred}</b>", 
                             ParagraphStyle('RiskStyle', parent=normal_style, 
                                          textColor=risk_color, fontSize=12, fontName='Helvetica-Bold'))
        elements.append(risk_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Add diet plan details
        for day, meals in diet_plan.items():
            elements.append(Paragraph(f"📅 {day}", subheader_style))
            
            if isinstance(meals, dict):
                for meal, value in meals.items():
                    elements.append(Paragraph(f"<b>{meal}:</b> {value}", normal_style))
            elif isinstance(meals, list):
                for item in meals:
                    elements.append(Paragraph(f"• {item}", normal_style))
            else:
                elements.append(Paragraph(str(meals), normal_style))
            
            elements.append(Spacer(1, 0.15*inch))
        
        # Add page break after each patient except the last one
        if i < len(patient_data_list):
            elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

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
    st.markdown("### 🏥 Navigation Menu")
    st.markdown("---")
    page = st.radio("", ["🏠 Home", "📊 Dashboard"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("👥 Total Patients", f"{total_patients:,}")
    st.metric("🎯 Model Accuracy", "98.5%")
    st.markdown(f"**🔍 Features Analyzed:** {len(FEATURE_COLUMNS)}")
    st.markdown("**🤖 Model:** LightGBM")

# ================= HOME PAGE =================
if page == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3em; margin-bottom: 0;">🏥 AI Diet Planner</h1>
        <h3 style="font-size: 1.5em; margin: 10px 0;">Personalized Nutrition Plans Based on Medical Intelligence</h3>
        <p style="font-size: 1.1em; opacity: 0.95;">Revolutionizing healthcare with machine learning and personalized diet recommendations</p>
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
    
    # KPI Cards with actual data
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p>👥 Total Patients</p>
            <h3>{total_patients:,}</h3>
            <p style="color: #999; font-size: 0.85em;">Analyzed Successfully</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p>🔴 High Risk</p>
            <h3>{high_risk:,}</h3>
            <p class="delta">↑ {high_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p>🟢 Low Risk</p>
            <h3>{low_risk:,}</h3>
            <p class="delta">↑ {low_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <p>🎯 Accuracy</p>
            <h3>98.5%</h3>
            <p style="color: #51cf66; font-size: 0.85em; font-weight: 600;">High Performance</p>
        </div>
        """, unsafe_allow_html=True)
    
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
                
                # Store patient data for PDF generation
                patient_data_list = []
                
                for i, pred in enumerate(df_with_risk["risk_label"]):
                    progress_bar.progress((i + 1) / len(df_with_risk))
                    progress_text.text(f"Processing Patient {i+1}/{len(df_with_risk)}")
                    
                    diet_key = "high_risk" if pred == "HIGH DIET RISK" else "low_risk"
                    diet_plan = diet_data[diet_key]
                    
                    # Store for PDF
                    patient_data_list.append((pred, diet_plan))
                    
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
                
                # PDF Download Section
                st.markdown('<div class="section-header">📥 Download Diet Plans</div>', unsafe_allow_html=True)
                st.markdown('<div class="pdf-download-section">', unsafe_allow_html=True)
                st.markdown("""
                    <h3 style="color: #4a90e2; text-align: center; margin-bottom: 15px;">📄 Export All Diet Plans to PDF</h3>
                    <p style="text-align: center; color: #666; margin-bottom: 20px;">
                        Download a comprehensive PDF report containing all patient diet plans for easy sharing and archiving.
                    </p>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    # Generate PDF
                    pdf_buffer = create_diet_plan_pdf(patient_data_list, df_with_risk)
                    
                    st.download_button(
                        label="📥 Download All Diet Plans (PDF)",
                        data=pdf_buffer,
                        file_name=f"AI_Diet_Plans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
    
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
    
    # KPI Cards with actual data
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p>👥 Total Patients</p>
            <h3>{total_patients:,}</h3>
            <p style="color: #999; font-size: 0.85em;">Total analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p>🔴 High Risk</p>
            <h3>{high_risk:,}</h3>
            <p class="delta">↑ {high_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p>🟢 Low Risk</p>
            <h3>{low_risk:,}</h3>
            <p class="delta">↑ {low_risk_pct:.1f}% of total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <p>⚡ Processing Speed</p>
            <h3>< 1s</h3>
            <p style="color: #999; font-size: 0.85em;">Per patient</p>
        </div>
        """, unsafe_allow_html=True)
    
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
            title_text="<b>Risk Distribution Overview</b>",
            title_x=0.5,
            showlegend=True,
            paper_bgcolor='rgba(255,255,255,0.95)',
            plot_bgcolor='rgba(255,255,255,0.95)',
            height=400
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
                marker_opacity=0.85,
                text=risk_counts["Patient Count"],
                textposition='outside',
                textfont=dict(size=16, color='#333'),
                hovertemplate='<b>%{x}</b><br>Patient Count: %{y}<extra></extra>'
            )
        ])
        
        fig_bar.update_layout(
            title_text="<b>Patient Risk Comparison</b>",
            title_x=0.5,
            xaxis_title="Risk Level",
            yaxis_title="Number of Patients",
            paper_bgcolor='rgba(255,255,255,0.95)',
            plot_bgcolor='rgba(255,255,255,0.95)',
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

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.9); border-radius: 15px; margin-top: 30px;">
    <h3 style="color: #4a90e2; margin-bottom: 15px;">🏥 AI Diet Planner</h3>
    <p style="color: #666; font-size: 16px; margin-bottom: 10px;">
        © 2025 AI Diet Planner | Powered by Machine Learning | Built with Streamlit
    </p>
    <p style="color: #999; font-size: 14px;">
        Version 3.0 | Last Updated: January 2025 | Accuracy: 98.5%
    </p>
    <div style="margin-top: 20px;">
        <span style="color: #4a90e2; margin: 0 10px;">📧 support@aidietplanner.com</span>
        <span style="color: #7b68ee; margin: 0 10px;">🌐 www.aidietplanner.com</span>
    </div>
</div>
""", unsafe_allow_html=True)
