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

# Custom CSS for modern, colorful design
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom cards */
    .custom-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Header styling */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #667eea !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
    }
    
    h3 {
        color: #764ba2 !important;
        font-weight: 600 !important;
    }
    
    h4 {
        color: #4facfe !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 5px solid #4facfe;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        font-weight: 600;
        color: #667eea;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    /* Custom badge */
    .badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 5px;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
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
    st.markdown("### 🩺 Health Status Assessment")
    st.markdown("")
    
    cols = st.columns(4)
    
    for idx, (key, data) in enumerate(metrics.items()):
        col = cols[idx % 4]
        
        status = data.get("status", "Normal")
        if status == "High":
            emoji = "🔴"
            badge_class = "badge-warning"
        elif status == "Low":
            emoji = "🟡"
            badge_class = "badge-warning"
        else:
            emoji = "🟢"
            badge_class = "badge-success"
        
        with col:
            st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 12px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; 
                        margin-bottom: 15px; border-top: 4px solid #667eea;'>
                <div style='font-size: 2rem;'>{emoji}</div>
                <div style='color: #667eea; font-weight: 600; margin: 10px 0; font-size: 0.9rem;'>
                    {key.upper().replace('_', ' ')}
                </div>
                <div style='font-size: 1.5rem; font-weight: 700; color: #333;'>
                    {data.get('value', 'N/A')}
                </div>
                <div style='color: #888; font-size: 0.85rem;'>{data.get('unit', '')}</div>
                <div class='badge {badge_class}' style='margin-top: 10px;'>{status}</div>
            </div>
            """, unsafe_allow_html=True)

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
        textColor=colors.HexColor('#667eea'),
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
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 0;'>🏥 AI Medical Diet Planner</h1>
        <p style='font-size: 1.3rem; color: white; font-weight: 300; margin-top: 0.5rem;'>
            Transform Your Health with Personalized Nutrition
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='color: white !important; font-size: 1.8rem;'>📋 How It Works</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin: 15px 0;'>
            <div style='margin: 15px 0;'>
                <div style='font-size: 2rem; margin-bottom: 5px;'>📤</div>
                <div style='font-weight: 600; font-size: 1.1rem;'>Upload Report</div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>Upload your medical PDF</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin: 15px 0;'>
            <div style='margin: 15px 0;'>
                <div style='font-size: 2rem; margin-bottom: 5px;'>🔍</div>
                <div style='font-weight: 600; font-size: 1.1rem;'>AI Analysis</div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>Extract health metrics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin: 15px 0;'>
            <div style='margin: 15px 0;'>
                <div style='font-size: 2rem; margin-bottom: 5px;'>🍽️</div>
                <div style='font-weight: 600; font-size: 1.1rem;'>Get Diet Plan</div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>Personalized recommendations</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin: 15px 0;'>
            <div style='margin: 15px 0;'>
                <div style='font-size: 2rem; margin-bottom: 5px;'>📥</div>
                <div style='font-weight: 600; font-size: 1.1rem;'>Download</div>
                <div style='font-size: 0.9rem; opacity: 0.9;'>Save your custom report</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; border-left: 4px solid white;'>
            <div style='font-weight: 600; margin-bottom: 8px;'>💡 Pro Tip</div>
            <div style='font-size: 0.9rem;'>Ensure your report contains BMI, cholesterol, blood sugar, and other standard metrics</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; border-left: 4px solid #FFD700;'>
            <div style='font-weight: 600; margin-bottom: 8px;'>⚠️ Disclaimer</div>
            <div style='font-size: 0.85rem;'>This tool provides general dietary guidance. Always consult healthcare professionals for medical advice.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("""
    <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); margin: 20px 0;'>
        <h3 style='color: #667eea; text-align: center; margin-bottom: 20px;'>📄 Upload Your Medical Report</h3>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=['pdf'],
        help="Upload a PDF file containing your medical test results",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        with st.spinner("🔍 Reading your medical report..."):
            report_text = extract_text_from_pdf(uploaded_file)
        
        if report_text:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                        padding: 15px 25px; border-radius: 10px; color: white; 
                        text-align: center; font-weight: 600; margin: 20px 0;'>
                ✅ Medical report uploaded successfully!
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📄 View Extracted Text", expanded=False):
                st.text_area("Report Content", report_text[:1000] + "..." if len(report_text) > 1000 else report_text, height=200)
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🚀 Generate Diet Plan", type="primary", use_container_width=True):
                    with st.spinner("📊 Analyzing your health metrics and creating personalized recommendations..."):
                        analysis = analyze_medical_report(report_text)
                    
                    if analysis:
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                    padding: 15px 25px; border-radius: 10px; color: white; 
                                    text-align: center; font-weight: 600; margin: 20px 0;'>
                            ✅ Analysis Complete! Your personalized plan is ready.
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<hr>", unsafe_allow_html=True)
                        
                        # Patient Information
                        st.markdown("""
                        <div style='background: white; padding: 25px; border-radius: 15px; 
                                    box-shadow: 0 8px 16px rgba(0,0,0,0.1); margin: 20px 0;'>
                            <h2 style='color: #667eea; margin-bottom: 20px;'>👤 Patient Information</h2>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 15px;'>
                                <div style='font-size: 2.5rem;'>👨‍⚕️</div>
                                <div style='color: #888; font-size: 0.9rem; margin-top: 8px;'>Name</div>
                                <div style='font-size: 1.3rem; font-weight: 700; color: #333;'
