import streamlit as st
import json
import PyPDF2
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

# Page configuration
st.set_page_config(
    page_title="AI Medical Diet Plan Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional medical website styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main color scheme - Professional Medical */
    :root {
        --primary-blue: #1565C0;
        --secondary-green: #2E7D32;
        --accent-teal: #00897B;
        --light-bg: #FAFAFA;
        --card-bg: #FFFFFF;
        --text-primary: #212121;
        --text-secondary: #757575;
        --border-color: #E0E0E0;
    }
    
    /* Global font */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(to bottom, #F5F7FA 0%, #FFFFFF 100%);
        padding: 0 !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }
    
    /* Headers */
    h1 {
        color: #1565C0 !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #2E7D32 !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        color: #1565C0 !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
    }
    
    h4 {
        color: #424242 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Professional Cards */
    .medical-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #E8EAF6;
        margin: 1.5rem 0;
        transition: box-shadow 0.3s ease;
    }
    
    .medical-card:hover {
        box-shadow: 0 4px 16px rgba(21, 101, 192, 0.12);
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(21, 101, 192, 0.2);
    }
    
    .hero-title {
        color: white !important;
        font-size: 2.75rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        color: #E3F2FD !important;
        font-size: 1.25rem !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1565C0 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #424242 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    div[data-testid="stMetricDelta"] {
        display: none !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.25) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0D47A1 0%, #01579B 100%) !important;
        box-shadow: 0 6px 16px rgba(21, 101, 192, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%) !important;
        box-shadow: 0 6px 16px rgba(46, 125, 50, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: white !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        border: 2px dashed #1565C0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: #1565C0 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D47A1 0%, #1565C0 100%) !important;
        padding-top: 1.5rem !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h2 {
        color: white !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        padding-bottom: 0.75rem;
        font-size: 1.3rem !important;
    }
    
    /* Step Cards in Sidebar */
    .step-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.6rem 0;
    }
    
    .step-card h3 {
        color: white !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.4rem !important;
        font-weight: 600 !important;
    }
    
    .step-card p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.8rem !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }
    
    /* Alert Boxes */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
    }
    
    .stSuccess {
        background: #E8F5E9 !important;
        border-left: 3px solid #2E7D32 !important;
        color: #1B5E20 !important;
    }
    
    .stSuccess [data-testid="stMarkdownContainer"] p {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        word-break: normal !important;
        overflow-wrap: break-word !important;
    }
    
    .stInfo {
        background: #E3F2FD !important;
        border-left: 3px solid #1565C0 !important;
        color: #0D47A1 !important;
    }
    
    .stInfo [data-testid="stMarkdownContainer"] p {
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
        word-break: normal !important;
        overflow-wrap: break-word !important;
    }
    
    .stWarning {
        background: #FFF3E0 !important;
        border-left: 3px solid #F57C00 !important;
        color: #E65100 !important;
    }
    
    .stWarning [data-testid="stMarkdownContainer"] p {
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
        word-break: normal !important;
        overflow-wrap: break-word !important;
    }
    
    .stError {
        background: #FFEBEE !important;
        border-left: 3px solid #D32F2F !important;
        color: #B71C1C !important;
    }
    
    .stError [data-testid="stMarkdownContainer"] p {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        word-break: normal !important;
        overflow-wrap: break-word !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #424242 !important;
        padding: 1rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #1565C0 !important;
        background: #F5F7FA !important;
    }
    
    /* Divider */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, #1565C0 0%, #2E7D32 50%, #00897B 100%) !important;
        margin: 2.5rem 0 !important;
        opacity: 0.3 !important;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #E3F2FD 0%, #E8F5E9 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1565C0;
        margin: 2rem 0 1.5rem 0;
    }
    
    .section-header h2 {
        margin: 0 !important;
        color: #1565C0 !important;
    }
    
    /* Text Areas */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 2px solid #E0E0E0 !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
        font-size: 0.875rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #1565C0 !important;
        box-shadow: 0 0 0 2px rgba(21, 101, 192, 0.1) !important;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #1565C0 !important;
    }
    
    /* Footer */
    .footer-section {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 2.5rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        border: 2px solid #2E7D32;
    }
    
    .footer-section h2 {
        color: #2E7D32 !important;
        margin-bottom: 0.75rem !important;
    }
    
    .footer-section p {
        color: #1B5E20;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* List Items */
    li {
        color: #424242 !important;
        line-height: 1.6 !important;
        margin: 0.4rem 0 !important;
        font-size: 0.9rem !important;
        word-break: normal !important;
        overflow-wrap: break-word !important;
    }
    
    /* Paragraph text fixes */
    p {
        word-break: normal !important;
        overflow-wrap: break-word !important;
        hyphens: auto !important;
    }
    
    /* Food list items */
    .food-item {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        padding: 0.5rem 0 !important;
        word-break: normal !important;
        overflow-wrap: break-word !important;
    }
    
    /* Professional Badge */
    .metric-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
    }
    
    .badge-high {
        background: #FFEBEE;
        color: #C62828;
        border: 1px solid #EF9A9A;
    }
    
    .badge-normal {
        background: #E8F5E9;
        color: #2E7D32;
        border: 1px solid #A5D6A7;
    }
    
    .badge-low {
        background: #FFF3E0;
        color: #EF6C00;
        border: 1px solid #FFCC80;
    }
</style>
""", unsafe_allow_html=True)

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# Extract health metrics using regex patterns
def extract_health_metrics(text):
    metrics = {}
    
    # Common patterns for health metrics
    patterns = {
        'bmi': r'BMI[:\s]+(\d+\.?\d*)',
        'cholesterol': r'(?:Total\s+)?Cholesterol[:\s]+(\d+)',
        'blood_sugar': r'(?:Blood\s+Sugar|Glucose|FBS|RBS)[:\s]+(\d+)',
        'blood_pressure': r'(?:Blood\s+Pressure|BP)[:\s]+(\d+/\d+)',
        'hemoglobin': r'(?:Hemoglobin|Hb|HGB)[:\s]+(\d+\.?\d*)',
        'triglycerides': r'Triglycerides[:\s]+(\d+)',
        'hdl': r'HDL[:\s]+(\d+)',
        'ldl': r'LDL[:\s]+(\d+)',
        'weight': r'Weight[:\s]+(\d+\.?\d*)',
        'height': r'Height[:\s]+(\d+\.?\d*)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metrics[key] = match.group(1)
    
    return metrics

# Determine health status based on values
def get_health_status(metric, value):
    try:
        val = float(value) if '/' not in str(value) else value
    except:
        return "Normal"
    
    ranges = {
        'bmi': {'low': 18.5, 'high': 24.9},
        'cholesterol': {'low': 0, 'high': 200},
        'blood_sugar': {'low': 70, 'high': 100},
        'hemoglobin': {'low': 12, 'high': 16},
        'triglycerides': {'low': 0, 'high': 150},
        'hdl': {'low': 40, 'high': 1000},
        'ldl': {'low': 0, 'high': 100},
    }
    
    if metric in ranges:
        if isinstance(val, str):
            return "Normal"
        if val < ranges[metric]['low']:
            return "Low"
        elif val > ranges[metric]['high']:
            return "High"
    
    return "Normal"

# Generate diet plan based on health conditions
def generate_diet_plan(metrics, diagnoses):
    has_diabetes = any('diabetes' in d.lower() for d in diagnoses)
    has_hypertension = any('hypertension' in d.lower() or 'pressure' in d.lower() for d in diagnoses)
    has_high_cholesterol = metrics.get('cholesterol_status') == 'High'
    
    # Base meal plan
    meal_plan = {
        'breakfast': [
            "Oatmeal with berries and chia seeds",
            "Greek yogurt with nuts and honey",
            "Whole grain toast with avocado"
        ],
        'lunch': [
            "Grilled chicken salad with olive oil dressing",
            "Quinoa bowl with roasted vegetables",
            "Brown rice with lentils and steamed broccoli"
        ],
        'dinner': [
            "Baked salmon with sweet potato",
            "Grilled fish with mixed vegetables",
            "Chicken breast with cauliflower rice"
        ],
        'snacks': [
            "Mixed nuts (almonds, walnuts)",
            "Fresh fruits (apple, orange, berries)",
            "Carrot and cucumber sticks with hummus"
        ]
    }
    
    # Customize based on conditions
    if has_diabetes:
        meal_plan['breakfast'].append("Sugar-free protein smoothie")
        meal_plan['snacks'].append("Celery with almond butter")
    
    if has_hypertension:
        meal_plan['lunch'].append("Low-sodium vegetable soup")
        meal_plan['dinner'].append("Herb-seasoned chicken (no salt)")
    
    return meal_plan

# Generate nutrition guidelines
def generate_nutrition_guidelines(diagnoses):
    has_diabetes = any('diabetes' in d.lower() for d in diagnoses)
    has_hypertension = any('hypertension' in d.lower() or 'pressure' in d.lower() for d in diagnoses)
    
    base_guidelines = {
        'daily_calories': 2000,
        'protein_g': 60,
        'carbs_g': 250,
        'fats_g': 70,
        'fiber_g': 30,
        'sodium_mg': 2300,
        'foods_to_include': [
            "Leafy green vegetables (spinach, kale)",
            "Whole grains (brown rice, quinoa, oats)",
            "Lean proteins (chicken, fish, legumes)",
            "Healthy fats (olive oil, avocado, nuts)",
            "Fresh fruits (berries, apples, citrus)"
        ],
        'foods_to_avoid': [
            "Processed foods and fast food",
            "Sugary drinks and desserts",
            "Refined carbohydrates (white bread, pasta)",
            "Trans fats and hydrogenated oils",
            "Excessive salt and sodium"
        ]
    }
    
    if has_diabetes:
        base_guidelines['carbs_g'] = 150
        base_guidelines['foods_to_avoid'].extend([
            "High-sugar fruits (mangoes, grapes)",
            "White rice and potatoes"
        ])
    
    if has_hypertension:
        base_guidelines['sodium_mg'] = 1500
        base_guidelines['foods_to_avoid'].extend([
            "Canned soups and processed meats",
            "Pickles and salty snacks"
        ])
    
    return base_guidelines

# Generate lifestyle recommendations
def generate_lifestyle_recommendations(diagnoses):
    has_diabetes = any('diabetes' in d.lower() for d in diagnoses)
    has_hypertension = any('hypertension' in d.lower() or 'pressure' in d.lower() for d in diagnoses)
    
    recommendations = {
        'exercise': [
            "30 minutes of brisk walking daily",
            "Yoga or stretching 3 times per week",
            "Light strength training 2 times per week"
        ],
        'sleep': "Aim for 7-8 hours of quality sleep each night. Maintain a consistent sleep schedule.",
        'stress_management': [
            "Practice deep breathing exercises",
            "Meditation for 10-15 minutes daily",
            "Engage in hobbies and relaxation activities"
        ],
        'hydration': "Drink 8-10 glasses (2-2.5 liters) of water daily. Start your day with a glass of water."
    }
    
    if has_diabetes:
        recommendations['exercise'].append("Monitor blood sugar before and after exercise")
    
    if has_hypertension:
        recommendations['exercise'].append("Avoid heavy lifting, focus on cardio")
    
    return recommendations

# Analyze medical report
def analyze_medical_report(report_text):
    # Extract metrics
    raw_metrics = extract_health_metrics(report_text)
    
    # Build structured health metrics
    health_metrics = {}
    units = {
        'bmi': 'kg/m²',
        'cholesterol': 'mg/dL',
        'blood_sugar': 'mg/dL',
        'blood_pressure': 'mmHg',
        'hemoglobin': 'g/dL',
        'triglycerides': 'mg/dL',
        'hdl': 'mg/dL',
        'ldl': 'mg/dL'
    }
    
    for metric, value in raw_metrics.items():
        if metric in units:
            status = get_health_status(metric, value)
            health_metrics[metric] = {
                'value': value,
                'status': status,
                'unit': units[metric]
            }
    
    # Extract patient info (basic extraction)
    name_match = re.search(r'(?:Name|Patient)[:\s]+([A-Za-z\s]+)', report_text, re.IGNORECASE)
    age_match = re.search(r'Age[:\s]+(\d+)', report_text, re.IGNORECASE)
    gender_match = re.search(r'(?:Gender|Sex)[:\s]+(Male|Female)', report_text, re.IGNORECASE)
    
    patient_info = {
        'name': name_match.group(1).strip() if name_match else "Patient",
        'age': int(age_match.group(1)) if age_match else 0,
        'gender': gender_match.group(1) if gender_match else "Unknown"
    }
    
    # Determine diagnoses based on metrics
    diagnoses = []
    if health_metrics.get('blood_sugar', {}).get('status') == 'High':
        diagnoses.append("Elevated Blood Sugar / Pre-diabetes Risk")
    if health_metrics.get('blood_pressure', {}).get('value', '120/80').split('/')[0] != '120':
        if int(health_metrics.get('blood_pressure', {}).get('value', '120/80').split('/')[0]) > 130:
            diagnoses.append("Hypertension (High Blood Pressure)")
    if health_metrics.get('cholesterol', {}).get('status') == 'High':
        diagnoses.append("High Cholesterol")
    if health_metrics.get('bmi', {}).get('status') == 'High':
        diagnoses.append("Overweight / Obesity")
    
    if not diagnoses:
        diagnoses = ["No significant conditions detected"]
    
    # Generate recommendations
    meal_plan = generate_diet_plan(health_metrics, diagnoses)
    nutrition_guidelines = generate_nutrition_guidelines(diagnoses)
    lifestyle_recommendations = generate_lifestyle_recommendations(diagnoses)
    
    return {
        'patient_info': patient_info,
        'health_metrics': health_metrics,
        'diagnoses': diagnoses,
        'meal_plan': meal_plan,
        'nutrition_guidelines': nutrition_guidelines,
        'lifestyle_recommendations': lifestyle_recommendations
    }

# Display health metrics with color coding
def display_health_metrics(metrics):
    st.markdown("<div class='section-header'><h2>🩺 Health Status Assessment</h2></div>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    for idx, (key, data) in enumerate(metrics.items()):
        col = cols[idx % 4]
        
        status = data.get("status", "Normal")
        if status == "High":
            color = "🔴"
        elif status == "Low":
            color = "🟡"
        else:
            color = "🟢"
        
        with col:
            st.metric(
                label=f"{color} {key.upper().replace('_', ' ')}",
                value=f"{data.get('value', 'N/A')} {data.get('unit', '')}"
            )

# Generate PDF report
def generate_pdf_report(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1565C0'),
        spaceAfter=30
    )
    story.append(Paragraph("Medical Diet Plan Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    story.append(Paragraph("<b>Patient Information</b>", styles['Heading2']))
    patient = data['patient_info']
    story.append(Paragraph(f"Name: {patient['name']}", styles['Normal']))
    story.append(Paragraph(f"Age: {patient['age']} | Gender: {patient['gender']}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Health Metrics
    story.append(Paragraph("<b>Health Metrics</b>", styles['Heading2']))
    for key, val in data['health_metrics'].items():
        story.append(Paragraph(
            f"{key.upper()}: {val['value']} {val['unit']} - {val['status']}", 
            styles['Normal']
        ))
    story.append(Spacer(1, 0.2*inch))
    
    # Diagnoses
    story.append(Paragraph("<b>Diagnoses</b>", styles['Heading2']))
    for diag in data['diagnoses']:
        story.append(Paragraph(f"• {diag}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Meal Plan
    story.append(Paragraph("<b>Personalized Meal Plan</b>", styles['Heading2']))
    for meal, items in data['meal_plan'].items():
        story.append(Paragraph(f"<b>{meal.upper()}:</b>", styles['Normal']))
        for item in items:
            story.append(Paragraph(f"  • {item}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Nutrition Guidelines
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Daily Nutrition Targets</b>", styles['Heading2']))
    nutrition = data['nutrition_guidelines']
    story.append(Paragraph(f"Calories: {nutrition['daily_calories']} kcal", styles['Normal']))
    story.append(Paragraph(f"Protein: {nutrition['protein_g']}g | Carbs: {nutrition['carbs_g']}g | Fats: {nutrition['fats_g']}g", styles['Normal']))
    story.append(Paragraph(f"Fiber: {nutrition['fiber_g']}g | Sodium: {nutrition['sodium_mg']}mg", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Main app
def main():
    # Hero Section
    st.markdown("""
    <div class='hero-section'>
        <h1 class='hero-title'>🏥 AI Medical Diet Plan Generator</h1>
        <p class='hero-subtitle'>
            Transform your medical reports into evidence-based, personalized nutrition plans
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>📋 How It Works</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("""
        <div class='step-card'>
            <h3>📤 Step 1</h3>
            <p>Upload your medical report in PDF format</p>
        </div>
        
        <div class='step-card'>
            <h3>🔍 Step 2</h3>
            <p>AI extracts health metrics automatically</p>
        </div>
        
        <div class='step-card'>
            <h3>🍽️ Step 3</h3>
            <p>Receive your personalized diet plan</p>
        </div>
        
        <div class='step-card'>
            <h3>📥 Step 4</h3>
            <p>Download your comprehensive report</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Required Metrics**\n\nYour report should contain standard health metrics like BMI, cholesterol, blood sugar, blood pressure, etc.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("⚠️ **Medical Disclaimer**\n\nThis tool provides general dietary guidance. Always consult healthcare professionals for personalized medical advice.")
    
    # File upload section
    st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
    st.markdown("### 📄 Upload Your Medical Report")
    st.markdown("<p style='color: #757575; margin-bottom: 1rem;'>Select a PDF file containing your laboratory test results and health metrics</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose PDF file", 
        type=['pdf'],
        help="Upload a PDF file with your lab results and health metrics",
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file:
        with st.spinner("🔍 Processing your medical report..."):
            report_text = extract_text_from_pdf(uploaded_file)
        
        if report_text:
            st.success("✅ Medical report uploaded and processed successfully")
            
            with st.expander("📄 View Extracted Report Text", expanded=False):
                st.text_area(
                    "Report Content", 
                    report_text[:1000] + "..." if len(report_text) > 1000 else report_text, 
                    height=200,
                    label_visibility="collapsed"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🚀 Generate Personalized Diet Plan", type="primary", use_container_width=True):
                    with st.spinner("🔬 Analyzing health data and generating recommendations..."):
                        analysis = analyze_medical_report(report_text)
                    
                    if analysis:
                        st.success("✅ Analysis complete! Your personalized plan is ready.")
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Patient Information
                        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-header'><h2>👤 Patient Information</h2></div>", unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📝 Name", analysis['patient_info']['name'])
                        with col2:
                            st.metric("🎂 Age", f"{analysis['patient_info']['age']} years" if analysis['patient_info']['age'] > 0 else "N/A")
                        with col3:
                            st.metric("⚧ Gender", analysis['patient_info']['gender'])
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Health Metrics
                        if analysis['health_metrics']:
                            st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
                            display_health_metrics(analysis['health_metrics'])
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ No health metrics detected in the report. Please ensure your PDF contains standard laboratory values.")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Diagnoses
                        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-header'><h2>🏥 Health Assessment</h2></div>", unsafe_allow_html=True)
                        for diag in analysis['diagnoses']:
                            if "No significant" in diag:
                                st.success(f"✅ {diag}")
                            else:
                                st.warning(f"⚠️ {diag}")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Meal Plan
                        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-header'><h2>🍽️ Personalized Meal Plan</h2></div>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🌅 Breakfast")
                            for item in analysis['meal_plan']['breakfast']:
                                st.markdown(f"<p style='color: #424242; padding: 0.3rem 0; line-height: 1.5; font-size: 0.9rem;'>• {item}</p>", unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("#### ☀️ Lunch")
                            for item in analysis['meal_plan']['lunch']:
                                st.markdown(f"<p style='color: #424242; padding: 0.3rem 0; line-height: 1.5; font-size: 0.9rem;'>• {item}</p>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("#### 🌙 Dinner")
                            for item in analysis['meal_plan']['dinner']:
                                st.markdown(f"<p style='color: #424242; padding: 0.3rem 0; line-height: 1.5; font-size: 0.9rem;'>• {item}</p>", unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("#### 🎁 Healthy Snacks")
                            for item in analysis['meal_plan']['snacks']:
                                st.markdown(f"<p style='color: #424242; padding: 0.3rem 0; line-height: 1.5; font-size: 0.9rem;'>• {item}</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Nutrition Guidelines
                        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-header'><h2>📈 Daily Nutrition Targets</h2></div>", unsafe_allow_html=True)
                        
                        nutrition = analysis['nutrition_guidelines']
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🔥 Calories", f"{nutrition['daily_calories']} kcal")
                            st.metric("🥩 Protein", f"{nutrition['protein_g']}g")
                        with col2:
                            st.metric("🍞 Carbohydrates", f"{nutrition['carbs_g']}g")
                            st.metric("🥑 Fats", f"{nutrition['fats_g']}g")
                        with col3:
                            st.metric("🌾 Fiber", f"{nutrition['fiber_g']}g")
                            st.metric("🧂 Sodium", f"{nutrition['sodium_mg']}mg")
                        
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### ✅ Foods to Include")
                            for food in nutrition['foods_to_include']:
                                st.markdown(f"<div class='food-item' style='background: #E8F5E9; padding: 0.6rem; border-radius: 6px; margin: 0.4rem 0; color: #1B5E20;'>✓ {food}</div>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("#### ❌ Foods to Avoid")
                            for food in nutrition['foods_to_avoid']:
                                st.markdown(f"<div class='food-item' style='background: #FFEBEE; padding: 0.6rem; border-radius: 6px; margin: 0.4rem 0; color: #B71C1C;'>✗ {food}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Lifestyle Recommendations
                        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-header'><h2>💪 Lifestyle Recommendations</h2></div>", unsafe_allow_html=True)
                        
                        lifestyle = analysis['lifestyle_recommendations']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🏃 Exercise Plan")
                            for exercise in lifestyle['exercise']:
                                st.markdown(f"<p style='color: #424242; padding: 0.3rem 0; line-height: 1.5; font-size: 0.9rem;'>• {exercise}</p>", unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("#### 😌 Stress Management")
                            for tip in lifestyle['stress_management']:
                                st.markdown(f"<p style='color: #424242; padding: 0.3rem 0; line-height: 1.5; font-size: 0.9rem;'>• {tip}</p>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("#### 😴 Sleep Recommendation")
                            st.info(lifestyle['sleep'])
                            
                            st.markdown("#### 💧 Hydration Guide")
                            st.info(lifestyle['hydration'])
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Download Options
                        st.markdown("<div class='medical-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-header'><h2>📥 Download Your Plan</h2></div>", unsafe_allow_html=True)
                        st.markdown("<p style='color: #757575; margin-bottom: 1.5rem;'>Save your personalized diet plan in your preferred format</p>", unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            json_str = json.dumps(analysis, indent=2)
                            st.download_button(
                                label="📄 Download JSON",
                                data=json_str,
                                file_name="diet_plan.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        with col2:
                            pdf_buffer = generate_pdf_report(analysis)
                            st.download_button(
                                label="📑 Download PDF",
                                data=pdf_buffer,
                                file_name="diet_plan_report.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        with col3:
                            if st.button("📤 Share Info", use_container_width=True):
                                st.info("💡 Share the downloaded PDF with your doctor or nutritionist for professional guidance!")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Success Footer
                        st.markdown("""
                        <div class='footer-section'>
                            <h2>🎉 Your Personalized Diet Plan is Ready!</h2>
                            <p>
                                Follow these evidence-based recommendations and consult with your healthcare provider 
                                for optimal results. Remember, consistency is key to achieving your health goals.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
