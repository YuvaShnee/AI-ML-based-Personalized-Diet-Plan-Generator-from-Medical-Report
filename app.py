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

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main color scheme - Medical Blue & Green */
    :root {
        --primary-color: #0066CC;
        --secondary-color: #00A86B;
        --accent-color: #FF6B6B;
        --background-light: #F0F8FF;
        --text-dark: #2C3E50;
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #E3F2FD 0%, #F1F8E9 100%);
    }
    
    /* Header styling */
    h1 {
        color: #0066CC !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        padding: 20px 0;
        border-bottom: 4px solid #00A86B;
    }
    
    h2 {
        color: #00A86B !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
    }
    
    h3 {
        color: #0066CC !important;
        font-weight: 500 !important;
    }
    
    h4 {
        color: #2C3E50 !important;
        font-weight: 500 !important;
    }
    
    /* Card styling for sections */
    .stAlert {
        border-radius: 15px !important;
        border-left: 5px solid #00A86B !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #0066CC !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #2C3E50 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0066CC 0%, #0052A3 100%) !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,102,204,0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,102,204,0.4) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00A86B 0%, #008556 100%) !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,168,107,0.3) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,168,107,0.4) !important;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: white !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 2px dashed #0066CC !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0066CC 0%, #0052A3 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #E3F2FD !important;
        border-left: 5px solid #0066CC !important;
        border-radius: 10px !important;
    }
    
    .stSuccess {
        background-color: #E8F5E9 !important;
        border-left: 5px solid #00A86B !important;
        border-radius: 10px !important;
    }
    
    .stWarning {
        background-color: #FFF3E0 !important;
        border-left: 5px solid #FF9800 !important;
        border-radius: 10px !important;
    }
    
    .stError {
        background-color: #FFEBEE !important;
        border-left: 5px solid #FF6B6B !important;
        border-radius: 10px !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #0066CC !important;
    }
    
    /* Divider */
    hr {
        border: none !important;
        height: 3px !important;
        background: linear-gradient(90deg, #0066CC 0%, #00A86B 100%) !important;
        margin: 30px 0 !important;
        border-radius: 5px !important;
    }
    
    /* Custom card class */
    .custom-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        margin: 15px 0;
        border-left: 5px solid #00A86B;
        transition: transform 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 2px solid #E3F2FD !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #0066CC !important;
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
    st.markdown("## 🩺 Health Status Assessment")
    
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
        textColor=colors.HexColor('#0066CC'),
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
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='font-size: 48px; margin-bottom: 10px;'>🏥 AI Medical Diet Plan Generator</h1>
        <p style='font-size: 20px; color: #555; margin-bottom: 30px;'>
            Transform your medical reports into personalized nutrition plans with AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: white !important;'>📋 Getting Started</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 10px 0;'>
            <h3 style='color: white !important;'>📤 Step 1</h3>
            <p style='color: white !important;'>Upload your medical report (PDF format)</p>
        </div>
        
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 10px 0;'>
            <h3 style='color: white !important;'>🔍 Step 2</h3>
            <p style='color: white !important;'>Our AI extracts health metrics automatically</p>
        </div>
        
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 10px 0;'>
            <h3 style='color: white !important;'>🍽️ Step 3</h3>
            <p style='color: white !important;'>Get your personalized diet plan</p>
        </div>
        
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 10px 0;'>
            <h3 style='color: white !important;'>📥 Step 4</h3>
            <p style='color: white !important;'>Download your custom report</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.info("💡 **Tip:** Your report should contain standard health metrics like BMI, cholesterol, blood sugar, etc.")
        
        st.markdown("---")
        st.warning("⚠️ **Medical Disclaimer**\n\nThis tool provides general dietary guidance based on your health metrics. Always consult qualified healthcare professionals for personalized medical advice and treatment.")
    
    # File upload section
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### 📄 Upload Your Medical Report")
    uploaded_file = st.file_uploader(
        "Choose a PDF file containing your medical test results", 
        type=['pdf'],
        help="Upload a PDF file with your lab results and health metrics"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file:
        with st.spinner("🔍 Reading your medical report..."):
            report_text = extract_text_from_pdf(uploaded_file)
        
        if report_text:
            st.success("✅ Medical report uploaded successfully!")
            
            with st.expander("📄 View Extracted Text"):
                st.text_area("Report Content", report_text[:1000] + "..." if len(report_text) > 1000 else report_text, height=200)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🚀 Generate Personalized Diet Plan", type="primary", use_container_width=True):
                    with st.spinner("🔬 Analyzing your health metrics and creating personalized recommendations..."):
                        analysis = analyze_medical_report(report_text)
                    
                    if analysis:
                        st.balloons()
                        st.success("✅ Analysis complete! Your personalized plan is ready.")
                        st.markdown("---")
                        
                        # Patient Information
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        st.markdown("## 👤 Patient Information")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📝 Name", analysis['patient_info']['name'])
                        with col2:
                            st.metric("🎂 Age", f"{analysis['patient_info']['age']} years")
                        with col3:
                            st.metric("⚧ Gender", analysis['patient_info']['gender'])
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Health Metrics
                        if analysis['health_metrics']:
                            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                            display_health_metrics(analysis['health_metrics'])
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown("---")
                        else:
                            st.warning("⚠️ No health metrics detected in the report. Please ensure your PDF contains standard lab values.")
                        
                        # Diagnoses
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        st.markdown("## 🏥 Health Assessment")
                        for diag in analysis['diagnoses']:
                            if "No significant" in diag:
                                st.success(f"✅ {diag}")
                            else:
                                st.warning(f"⚠️ {diag}")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Meal Plan
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        st.markdown("## 🍽️ Personalized Meal Plan")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🌅 Breakfast")
                            for item in analysis['meal_plan']['breakfast']:
                                st.markdown(f"<p style='color: #2C3E50; padding: 5px 0;'>• {item}</p>", unsafe_allow_html=True)
                            
                            st.markdown("#### ☀️ Lunch")
                            for item in analysis['meal_plan']['lunch']:
                                st.markdown(f"<p style='color: #2C3E50; padding: 5px 0;'>• {item}</p>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("#### 🌙 Dinner")
                            for item in analysis['meal_plan']['dinner']:
                                st.markdown(f"<p style='color: #2C3E50; padding: 5px 0;'>• {item}</p>", unsafe_allow_html=True)
                            
                            st.markdown("#### 🎁 Snacks")
                            for item in analysis['meal_plan']['snacks']:
                                st.markdown(f"<p style='color: #2C3E50; padding: 5px 0;'>• {item}</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Nutrition Guidelines
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        st.markdown("## 📈 Daily Nutrition Targets")
                        
                        nutrition = analysis['nutrition_guidelines']
                        
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
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### ✅ Foods to Include")
                            for food in nutrition['foods_to_include']:
                                st.success(f"✓ {food}")
                        
                        with col2:
                            st.markdown("#### ❌ Foods to Avoid")
                            for food in nutrition['foods_to_avoid']:
                                st.error(f"✗ {food}")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Lifestyle Recommendations
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        st.markdown("## 💪 Lifestyle Recommendations")
                        
                        lifestyle = analysis['lifestyle_recommendations']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🏃 Exercise Plan")
                            for exercise in lifestyle['exercise']:
                                st.markdown(f"<p style='color: #2C3E50; padding: 5px 0;'>• {exercise}</p>", unsafe_allow_html=True)
                            
                            st.markdown("#### 😌 Stress Management")
                            for tip in lifestyle['stress_management']:
                                st.markdown(f"<p style='color: #2C3E50; padding: 5px 0;'>• {tip}</p>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("#### 😴 Sleep Recommendation")
                            st.info(lifestyle['sleep'])
                            
                            st.markdown("#### 💧 Hydration Guide")
                            st.info(lifestyle['hydration'])
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Download Options
                        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                        st.markdown("## 📥 Download Your Personalized Plan")
                        
                        col1, col2, col3 = st.columns([1,1,1])
                        
                        with col1:
                            # JSON Download
                            json_str = json.dumps(analysis, indent=2)
                            st.download_button(
                                label="📄 Download JSON",
                                data=json_str,
                                file_name="diet_plan.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        with col2:
                            # PDF Download
                            pdf_buffer = generate_pdf_report(analysis)
                            st.download_button(
                                label="📑 Download PDF",
                                data=pdf_buffer,
                                file_name="diet_plan_report.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        with col3:
                            # Share button (placeholder)
                            if st.button("📤 Share Report", use_container_width=True):
                                st.info("💡 You can share the downloaded PDF with your doctor or nutritionist!")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.markdown("""
                        <div style='text-align: center; background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); 
                                    padding: 30px; border-radius: 15px; margin: 20px 0;'>
                            <h2 style='color: #00A86B;'>🎉 Your Personalized Diet Plan is Ready!</h2>
                            <p style='color: #2C3E50; font-size: 18px;'>
                                Follow these recommendations and consult with your healthcare provider for best results.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
