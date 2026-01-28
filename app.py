import streamlit as st
import json
from pypdf import PdfReader
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="AI Medical Diet Plan Generator",
    page_icon="🏥",
    layout="wide"
)

# Add professional background colors
st.markdown("""
<style>
    /* Main background gradient */
    .main {
        background: linear-gradient(135deg, #E8EAF6 0%, #F3E5F5 50%, #E1F5FE 100%);
    }
    
    /* Responsive container */
    .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1565C0 0%, #0D47A1 100%);
    }
    
    /* Cards and containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px dashed #1565C0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Metric containers */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 0.75rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
    
    /* Adjust metric value size */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }
    
    /* Headers styling */
    h1 {
        color: #1565C0;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #2E7D32;
        font-size: 1.5rem !important;
        margin-top: 1rem !important;
    }
    
    h3 {
        color: #1565C0;
        font-size: 1.2rem !important;
    }
    
    h4 {
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Paragraph and text sizing */
    p {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }
    
    /* List items */
    li {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.3);
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(21, 101, 192, 0.4);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3);
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(46, 125, 50, 0.4);
    }
    
    /* Alert boxes */
    .stSuccess {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid #2E7D32;
        border-radius: 8px;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #1565C0;
        border-radius: 8px;
        padding: 0.75rem !important;
        font-size: 0.85rem !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-left: 4px solid #F57C00;
        border-radius: 8px;
        padding: 0.75rem !important;
        font-size: 0.85rem !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 4px solid #D32F2F;
        border-radius: 8px;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        font-size: 0.9rem !important;
        padding: 0.75rem !important;
    }
    
    /* Text area */
    .stTextArea textarea {
        font-size: 0.85rem !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #1565C0 0%, #2E7D32 50%, #00897B 100%);
        opacity: 0.5;
        margin: 1.5rem 0 !important;
    }
    
    /* Sidebar text sizing */
    [data-testid="stSidebar"] .stMarkdown {
        font-size: 0.85rem !important;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 1.3rem !important;
    }
    
    /* Spacing adjustments */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Column spacing */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Extract text from PDF with OCR support
def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF file with OCR support for image-based PDFs.
    Works with both text-based and scanned/image-based PDFs.
    """
    try:
        # Reset file pointer to beginning
        pdf_file.seek(0)
        
        # Read PDF bytes
        pdf_bytes = pdf_file.read()
        
        # Try regular text extraction first
        try:
            pdf_reader = PdfReader(BytesIO(pdf_bytes))
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as page_error:
                    continue
            
            # If we got substantial text, return it
            if text and len(text.strip()) > 50:
                return text
            
        except Exception as e:
            st.info("📄 Regular text extraction didn't work. Trying OCR...")
        
        # If regular extraction failed or got minimal text, try OCR
        st.info("🔍 Detecting image-based PDF. Using OCR to extract text...")
        
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes, dpi=300)
            
            text = ""
            total_pages = len(images)
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, image in enumerate(images):
                status_text.text(f"Processing page {i+1} of {total_pages}...")
                progress_bar.progress((i + 1) / total_pages)
                
                # Use pytesseract for OCR
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += f"\n--- Page {i+1} ---\n{page_text}\n"
            
            progress_bar.empty()
            status_text.empty()
            
            if text and len(text.strip()) > 50:
                st.success("✅ Text extracted successfully using OCR!")
                return text
            else:
                st.warning("⚠️ OCR completed but minimal text was found.")
                return None
                
        except Exception as ocr_error:
            st.error(f"❌ OCR failed: {str(ocr_error)}")
            st.info("💡 Make sure the PDF contains readable text or images.")
            return None
            
    except Exception as e:
        st.error(f"❌ Error reading PDF file: {str(e)}")
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
    st.subheader("🩺 Health Status Assessment")
    
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
        textColor=colors.HexColor('#1f77b4'),
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
    st.title("🏥 Medical Diet Plan Generator")
    st.markdown("### Upload your medical report to get personalized diet recommendations")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 How It Works")
        st.markdown("""
        1. **Upload** your medical report (PDF)
        2. **Extract** health metrics automatically
        3. **Get** personalized diet plan
        4. **Download** your custom report
        """)
        st.markdown("---")
        st.info("💡 Works with both text-based and scanned PDFs using OCR technology!")
        
        st.markdown("---")
        st.warning("⚠️ **Disclaimer**: This tool provides general dietary guidance. Always consult healthcare professionals for medical advice.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📄 Upload Medical Report (PDF)", 
        type=['pdf'],
        help="Upload a PDF file containing your medical test results (text-based or scanned)"
    )
    
    if uploaded_file:
        with st.spinner("🔍 Reading your medical report..."):
            report_text = extract_text_from_pdf(uploaded_file)
        
        if report_text:
            st.success("✅ Medical report uploaded successfully!")
            
            with st.expander("📄 View Extracted Text"):
                st.text_area("Report Content", report_text[:1000] + "..." if len(report_text) > 1000 else report_text, height=200)
            
            if st.button("🚀 Generate Diet Plan", type="primary", use_container_width=True):
                with st.spinner("📊 Analyzing your health metrics and creating personalized recommendations..."):
                    analysis = analyze_medical_report(report_text)
                
                if analysis:
                    st.success("✅ Analysis complete!")
                    st.markdown("---")
                    
                    # Patient Information
                    st.header("👤 Patient Information")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Name", analysis['patient_info']['name'])
                    with col2:
                        st.metric("Age", analysis['patient_info']['age'])
                    with col3:
                        st.metric("Gender", analysis['patient_info']['gender'])
                    
                    st.markdown("---")
                    
                    # Health Metrics
                    if analysis['health_metrics']:
                        display_health_metrics(analysis['health_metrics'])
                        st.markdown("---")
                    else:
                        st.warning("⚠️ No health metrics detected in the report. Please ensure your PDF contains standard lab values.")
                    
                    # Diagnoses
                    st.subheader("🏥 Health Assessment")
                    for diag in analysis['diagnoses']:
                        if "No significant" in diag:
                            st.success(f"✅ {diag}")
                        else:
                            st.warning(f"⚠️ {diag}")
                    
                    st.markdown("---")
                    
                    # Meal Plan
                    st.subheader("🍽️ Personalized Meal Plan")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 🌅 Breakfast")
                        for item in analysis['meal_plan']['breakfast']:
                            st.write(f"• {item}")
                        
                        st.markdown("#### ☀️ Lunch")
                        for item in analysis['meal_plan']['lunch']:
                            st.write(f"• {item}")
                    
                    with col2:
                        st.markdown("#### 🌙 Dinner")
                        for item in analysis['meal_plan']['dinner']:
                            st.write(f"• {item}")
                        
                        st.markdown("#### 🎁 Snacks")
                        for item in analysis['meal_plan']['snacks']:
                            st.write(f"• {item}")
                    
                    st.markdown("---")
                    
                    # Nutrition Guidelines
                    st.subheader("📈 Daily Nutrition Targets")
                    
                    nutrition = analysis['nutrition_guidelines']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Calories", f"{nutrition['daily_calories']} kcal")
                        st.metric("Protein", f"{nutrition['protein_g']}g")
                    with col2:
                        st.metric("Carbohydrates", f"{nutrition['carbs_g']}g")
                        st.metric("Fats", f"{nutrition['fats_g']}g")
                    with col3:
                        st.metric("Fiber", f"{nutrition['fiber_g']}g")
                        st.metric("Sodium", f"{nutrition['sodium_mg']}mg")
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### ✅ Foods to Include")
                        for food in nutrition['foods_to_include']:
                            st.success(f"✓ {food}")
                    
                    with col2:
                        st.markdown("#### ❌ Foods to Avoid")
                        for food in nutrition['foods_to_avoid']:
                            st.error(f"✗ {food}")
                    
                    st.markdown("---")
                    
                    # Lifestyle Recommendations
                    st.subheader("💪 Lifestyle Recommendations")
                    
                    lifestyle = analysis['lifestyle_recommendations']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 🏃 Exercise Plan")
                        for exercise in lifestyle['exercise']:
                            st.write(f"• {exercise}")
                        
                        st.markdown("#### 😌 Stress Management")
                        for tip in lifestyle['stress_management']:
                            st.write(f"• {tip}")
                    
                    with col2:
                        st.markdown("#### 😴 Sleep Recommendation")
                        st.info(lifestyle['sleep'])
                        
                        st.markdown("#### 💧 Hydration Guide")
                        st.info(lifestyle['hydration'])
                    
                    st.markdown("---")
                    
                    # Download Options
                    st.subheader("📥 Download Your Personalized Plan")
                    
                    col1, col2 = st.columns(2)
                    
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
                    
                    st.markdown("---")
                    st.success("🎉 Your personalized diet plan is ready!")

if __name__ == "__main__":
    main()
