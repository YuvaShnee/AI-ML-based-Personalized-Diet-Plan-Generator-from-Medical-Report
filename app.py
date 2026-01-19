
import streamlit as st
import anthropic
import json
import base64
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
import os

# Page configuration
st.set_page_config(
    page_title="AI Diet Plan Generator",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
    }
    .stButton>button {
        background-color: #10b981;
        color: white;
        font-weight: bold;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #059669;
    }
    .warning-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-left: 4px solid #f59e0b;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0fdf4;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #86efac;
        margin: 0.5rem 0;
    }
    .food-card {
        background-color: #f9fafb;
        padding: 0.75rem;
        border-left: 3px solid #10b981;
        border-radius: 0.375rem;
        margin: 0.5rem 0;
    }
    h1 {
        color: #047857;
    }
    h2 {
        color: #059669;
        margin-top: 2rem;
    }
    h3 {
        color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'diet_plan' not in st.session_state:
    st.session_state.diet_plan = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('ANTHROPIC_API_KEY', '')

def analyze_medical_report(pdf_file, api_key):
    """Analyze medical report using Claude API"""
    try:
        # Read PDF and convert to base64
        pdf_data = pdf_file.read()
        base64_pdf = base64.standard_b64encode(pdf_data).decode('utf-8')
        
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Create message with document
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": base64_pdf
                            }
                        },
                        {
                            "type": "text",
                            "text": """Analyze this medical report and create a comprehensive personalized diet plan. 

Please extract and analyze:
1. Key health metrics (blood sugar, cholesterol, vitamins, minerals, etc.)
2. Medical conditions or concerns identified
3. Any deficiencies or abnormal values

Then provide a detailed response in JSON format with this structure:
{
  "patientInfo": {
    "conditions": ["list of identified conditions"],
    "deficiencies": ["list of deficiencies"],
    "keyMetrics": {"metric": "value and status"}
  },
  "dietaryRecommendations": {
    "foodsToInclude": ["detailed list with reasons"],
    "foodsToAvoid": ["detailed list with reasons"],
    "supplementsSuggested": ["list if needed"]
  },
  "mealPlan": {
    "breakfast": ["option 1", "option 2", "option 3"],
    "lunch": ["option 1", "option 2", "option 3"],
    "dinner": ["option 1", "option 2", "option 3"],
    "snacks": ["option 1", "option 2", "option 3"]
  },
  "nutritionGuidelines": {
    "dailyCalories": "recommended range",
    "macroDistribution": {"protein": "x%", "carbs": "y%", "fats": "z%"},
    "hydration": "water intake recommendation"
  },
  "lifestyle": {
    "exerciseRecommendations": "exercise suggestions",
    "sleepGuidelines": "sleep recommendations",
    "stressManagement": "stress tips"
  },
  "warnings": ["important precautions or warnings"],
  "generalAdvice": "overall health advice"
}

Ensure all recommendations are evidence-based and appropriate for the conditions identified. Return ONLY the JSON, no other text."""
                        }
                    ]
                }
            ]
        )
        
        # Extract text from response
        response_text = message.content[0].text
        
        # Parse JSON from response
        # Try to find JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            diet_plan = json.loads(json_str)
            return diet_plan, None
        else:
            return None, "Could not parse diet plan from AI response"
            
    except Exception as e:
        return None, f"Error analyzing report: {str(e)}"

def generate_pdf(diet_plan):
    """Generate PDF report of the diet plan"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#10b981'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#059669'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#047857'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("🍏 Personalized Diet Plan", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Warnings
    if diet_plan.get('warnings'):
        story.append(Paragraph("⚠️ Important Warnings", heading_style))
        for warning in diet_plan['warnings']:
            story.append(Paragraph(f"• {warning}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Health Analysis
    story.append(Paragraph("📊 Health Analysis", heading_style))
    
    story.append(Paragraph("Identified Conditions", subheading_style))
    for condition in diet_plan['patientInfo']['conditions']:
        story.append(Paragraph(f"• {condition}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    if diet_plan['patientInfo']['deficiencies']:
        story.append(Paragraph("Deficiencies", subheading_style))
        for deficiency in diet_plan['patientInfo']['deficiencies']:
            story.append(Paragraph(f"• {deficiency}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Key Metrics", subheading_style))
    for metric, value in diet_plan['patientInfo']['keyMetrics'].items():
        story.append(Paragraph(f"<b>{metric}:</b> {value}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Dietary Recommendations
    story.append(Paragraph("🥗 Dietary Recommendations", heading_style))
    
    story.append(Paragraph("Foods to Include", subheading_style))
    for food in diet_plan['dietaryRecommendations']['foodsToInclude']:
        story.append(Paragraph(f"• {food}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("Foods to Avoid", subheading_style))
    for food in diet_plan['dietaryRecommendations']['foodsToAvoid']:
        story.append(Paragraph(f"• {food}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    if diet_plan['dietaryRecommendations']['supplementsSuggested']:
        story.append(Paragraph("Suggested Supplements", subheading_style))
        for supplement in diet_plan['dietaryRecommendations']['supplementsSuggested']:
            story.append(Paragraph(f"• {supplement}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Meal Plan
    story.append(Paragraph("🍽️ Sample Meal Plan", heading_style))
    
    for meal_type, options in diet_plan['mealPlan'].items():
        story.append(Paragraph(f"{meal_type.capitalize()} Options", subheading_style))
        for i, option in enumerate(options, 1):
            story.append(Paragraph(f"{i}. {option}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Nutrition Guidelines
    story.append(Paragraph("📈 Nutrition Guidelines", heading_style))
    story.append(Paragraph(f"<b>Daily Calories:</b> {diet_plan['nutritionGuidelines']['dailyCalories']}", styles['Normal']))
    
    story.append(Paragraph("<b>Macro Distribution:</b>", styles['Normal']))
    for macro, percentage in diet_plan['nutritionGuidelines']['macroDistribution'].items():
        story.append(Paragraph(f"• {macro.capitalize()}: {percentage}", styles['Normal']))
    
    story.append(Paragraph(f"<b>Hydration:</b> {diet_plan['nutritionGuidelines']['hydration']}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Lifestyle Recommendations
    story.append(Paragraph("💪 Lifestyle Recommendations", heading_style))
    story.append(Paragraph(f"<b>Exercise:</b> {diet_plan['lifestyle']['exerciseRecommendations']}", styles['Normal']))
    story.append(Paragraph(f"<b>Sleep:</b> {diet_plan['lifestyle']['sleepGuidelines']}", styles['Normal']))
    story.append(Paragraph(f"<b>Stress Management:</b> {diet_plan['lifestyle']['stressManagement']}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # General Advice
    story.append(Paragraph("💡 General Advice", heading_style))
    story.append(Paragraph(diet_plan['generalAdvice'], styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#6b7280'),
        alignment=TA_CENTER
    )
    story.append(Paragraph("<b>Disclaimer:</b> This diet plan is AI-generated based on medical report analysis. Please consult with healthcare professionals before making significant dietary changes.", disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Main App
st.title("🍏 AI-Powered Diet Plan Generator")
st.markdown("### Upload your medical report for personalized nutrition recommendations")

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input(
        "Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        help="Enter your Anthropic API key. Get one at https://console.anthropic.com/"
    )
    
    if api_key_input:
        st.session_state.api_key = api_key_input
    
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
    This app uses AI to analyze your medical reports and generate:
    - Personalized diet recommendations
    - Sample meal plans
    - Nutrition guidelines
    - Lifestyle advice
    
    **Supported formats:** PDF medical reports
    """)
    
    if st.session_state.diet_plan:
        st.markdown("---")
        st.success("✅ Diet plan generated!")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### 📄 Upload Medical Report")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload blood test results, health checkups, or other medical reports"
    )
    
    if uploaded_file and st.session_state.api_key:
        if st.button("🔍 Analyze Report & Generate Diet Plan", use_container_width=True):
            with st.spinner("🤖 AI is analyzing your medical report and creating personalized recommendations..."):
                diet_plan, error = analyze_medical_report(uploaded_file, st.session_state.api_key)
                
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.diet_plan = diet_plan
                    st.success("✅ Diet plan generated successfully!")
                    st.rerun()
    elif uploaded_file and not st.session_state.api_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar to analyze the report.")

with col2:
    if st.session_state.diet_plan:
        st.markdown("#### 📥 Export Options")
        
        # JSON Export
        json_data = json.dumps(st.session_state.diet_plan, indent=2)
        st.download_button(
            label="📊 Download JSON",
            data=json_data,
            file_name=f"diet-plan-{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        # PDF Export
        try:
            pdf_buffer = generate_pdf(st.session_state.diet_plan)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_buffer,
                file_name=f"diet-plan-{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF generation error: {str(e)}")

# Display Results
if st.session_state.diet_plan:
    diet_plan = st.session_state.diet_plan
    
    st.markdown("---")
    
    # Warnings
    if diet_plan.get('warnings'):
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Important Warnings")
        for warning in diet_plan['warnings']:
            st.markdown(f"- {warning}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Health Analysis
    st.markdown("## 📊 Health Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Identified Conditions")
        for condition in diet_plan['patientInfo']['conditions']:
            st.markdown(f'<div class="food-card">🔴 {condition}</div>', unsafe_allow_html=True)
    
    with col2:
        if diet_plan['patientInfo']['deficiencies']:
            st.markdown("### Deficiencies")
            for deficiency in diet_plan['patientInfo']['deficiencies']:
                st.markdown(f'<div class="food-card">🟠 {deficiency}</div>', unsafe_allow_html=True)
    
    st.markdown("### Key Metrics")
    metrics_cols = st.columns(2)
    for idx, (metric, value) in enumerate(diet_plan['patientInfo']['keyMetrics'].items()):
        with metrics_cols[idx % 2]:
            st.markdown(f'<div class="metric-card"><b>{metric}:</b> {value}</div>', unsafe_allow_html=True)
    
    # Dietary Recommendations
    st.markdown("## 🥗 Dietary Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Foods to Include")
        for food in diet_plan['dietaryRecommendations']['foodsToInclude']:
            st.markdown(f'<div class="food-card">{food}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ❌ Foods to Avoid")
        for food in diet_plan['dietaryRecommendations']['foodsToAvoid']:
            st.markdown(f'<div class="food-card">{food}</div>', unsafe_allow_html=True)
    
    if diet_plan['dietaryRecommendations']['supplementsSuggested']:
        st.markdown("### 💊 Suggested Supplements")
        supp_text = " • ".join(diet_plan['dietaryRecommendations']['supplementsSuggested'])
        st.info(supp_text)
    
    # Meal Plan
    st.markdown("## 🍽️ Sample Meal Plan")
    
    meal_cols = st.columns(2)
    for idx, (meal_type, options) in enumerate(diet_plan['mealPlan'].items()):
        with meal_cols[idx % 2]:
            st.markdown(f"### {meal_type.capitalize()}")
            for i, option in enumerate(options, 1):
                st.markdown(f'<div class="food-card"><b>Option {i}:</b> {option}</div>', unsafe_allow_html=True)
    
    # Nutrition Guidelines
    st.markdown("## 📈 Nutrition Guidelines")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Daily Calories", diet_plan['nutritionGuidelines']['dailyCalories'])
    
    with col2:
        macros = diet_plan['nutritionGuidelines']['macroDistribution']
        st.markdown("**Macro Distribution:**")
        for macro, percentage in macros.items():
            st.markdown(f"- {macro.capitalize()}: **{percentage}**")
    
    with col3:
        st.metric("Hydration", diet_plan['nutritionGuidelines']['hydration'])
    
    # Lifestyle Recommendations
    st.markdown("## 💪 Lifestyle Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏃 Exercise")
        st.info(diet_plan['lifestyle']['exerciseRecommendations'])
    
    with col2:
        st.markdown("### 😴 Sleep")
        st.info(diet_plan['lifestyle']['sleepGuidelines'])
    
    with col3:
        st.markdown("### 🧘 Stress Management")
        st.info(diet_plan['lifestyle']['stressManagement'])
    
    # General Advice
    st.markdown("## 💡 General Advice")
    st.success(diet_plan['generalAdvice'])
    
    # Disclaimer
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** This diet plan is AI-generated based on medical report analysis. Please consult with healthcare professionals before making significant dietary changes.")
else:
    # Welcome message
    st.info("👆 Upload a medical report PDF to get started!")
    
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. **Upload** your medical report (PDF format)
        2. **AI Analysis** extracts health metrics and identifies conditions
        3. **Personalized Plan** generated with:
           - Foods to include and avoid
           - Sample meal plans
           - Nutrition guidelines
           - Lifestyle recommendations
        4. **Export** your plan as PDF or JSON
        
        The AI analyzes blood test results, vitamin levels, cholesterol, blood sugar, and other health markers to create evidence-based recommendations.
        """)
