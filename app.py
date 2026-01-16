import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="AI Diet Planner",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    /* Feature card */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.25);
    }
    
    /* Header styling */
    .main-header {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        color: #667eea;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #4a5568;
        font-size: 1.2rem;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Risk badge */
    .risk-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1rem;
        margin: 1rem 0;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = None
if 'selected_patient' not in st.session_state:
    st.session_state.selected_patient = None

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🏥 Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
    
    if st.button("📊 Patient Data", use_container_width=True):
        st.session_state.page = 'data'
    
    if st.button("🍽️ Diet Plans", use_container_width=True):
        st.session_state.page = 'plans'
    
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.page = 'analytics'
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **AI-Powered Diet Planner**
    
    Version 2.0
    
    Revolutionizing healthcare with machine learning and personalized nutrition.
    """)

# Sample data generator (optimized for speed)
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    n_patients = 10
    
    data = {
        'patient_id': range(n_patients),
        'age': np.random.randint(20, 80, n_patients),
        'bmi': np.round(np.random.uniform(18, 40, n_patients), 2),
        'cholesterol': np.round(np.random.uniform(150, 350, n_patients), 2),
        'blood_sugar': np.round(np.random.uniform(70, 300, n_patients), 2),
        'hemoglobin': np.round(np.random.uniform(8, 18, n_patients), 2),
        'rbc_count': np.round(np.random.uniform(3.5, 6, n_patients), 2),
        'platelet_count': np.round(np.random.uniform(150, 400, n_patients), 2),
        'wbc_count': np.round(np.random.uniform(4, 11, n_patients), 2),
        'alkaline_phosphatase': np.round(np.random.uniform(40, 150, n_patients), 2),
        'total_protein': np.round(np.random.uniform(60, 85, n_patients), 2),
        'glucose': np.round(np.random.uniform(70, 200, n_patients), 2),
        'tumor_size': np.round(np.random.uniform(0, 5, n_patients), 2)
    }
    
    return pd.DataFrame(data)

# Diet plan generator
def generate_diet_plan(patient_id, bmi, cholesterol, blood_sugar):
    # Determine risk level
    risk_level = "LOW"
    if bmi > 30 or cholesterol > 240 or blood_sugar > 200:
        risk_level = "HIGH"
    elif bmi > 25 or cholesterol > 200 or blood_sugar > 140:
        risk_level = "MEDIUM"
    
    # Generate personalized plan
    breakfast = "Oatmeal with fruits and nuts" if bmi > 25 else "Whole grain toast with avocado"
    lunch = "Steamed vegetables with brown rice" if cholesterol > 200 else "Grilled chicken salad"
    snack = "Carrot sticks, nuts" if blood_sugar > 140 else "Greek yogurt with berries"
    dinner = "Baked fish with quinoa" if cholesterol > 200 else "Lean protein with vegetables"
    
    return {
        'patient_id': patient_id,
        'risk_level': risk_level,
        'breakfast': breakfast,
        'lunch': lunch,
        'snack': snack,
        'dinner': dinner
    }

# HOME PAGE
if st.session_state.page == 'home':
    st.markdown("""
        <div class="main-header">
            <h1>🍎 AI-Powered Diet Planner</h1>
            <p>Personalized Nutrition Plans Based on Medical Intelligence</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h2>🤖</h2>
                <h3>AI-Powered Analysis</h3>
                <p>Advanced machine learning algorithms analyze medical data to predict diet risks</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h2>🍏</h2>
                <h3>Personalized Plans</h3>
                <p>Custom diet recommendations tailored to individual health profiles</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <h2>📊</h2>
                <h3>Real-time Insights</h3>
                <p>Instant risk assessment and actionable dietary guidelines</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick start section
    st.markdown("""
        <div class="card">
            <h2>🚀 Quick Start Guide</h2>
            <ol>
                <li><strong>Upload Patient Data:</strong> Navigate to Patient Data to view medical records</li>
                <li><strong>Generate Diet Plans:</strong> Go to Diet Plans to create personalized nutrition plans</li>
                <li><strong>Analyze Results:</strong> View Analytics for comprehensive insights</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

# PATIENT DATA PAGE
elif st.session_state.page == 'data':
    st.markdown("""
        <div class="main-header">
            <h1>📊 Patient Medical Data Overview</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate and display data
    with st.spinner("Loading patient data..."):
        df = generate_sample_data()
        st.session_state.patient_data = df
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", len(df), delta=None)
    with col2:
        st.metric("Avg Age", f"{df['age'].mean():.1f}", delta=None)
    with col3:
        st.metric("Avg BMI", f"{df['bmi'].mean():.1f}", delta=None)
    with col4:
        st.metric("Avg Cholesterol", f"{df['cholesterol'].mean():.1f}", delta=None)

# DIET PLANS PAGE
elif st.session_state.page == 'plans':
    st.markdown("""
        <div class="main-header">
            <h1>🍽️ Personalized Diet Plans</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.patient_data is None:
        st.session_state.patient_data = generate_sample_data()
    
    df = st.session_state.patient_data
    
    # Patient selection
    st.markdown('<div class="card">', unsafe_allow_html=True)
    patient_id = st.selectbox("Select Patient ID", df['patient_id'].tolist())
    
    if st.button("🎯 Generate Diet Plan", use_container_width=True):
        patient = df[df['patient_id'] == patient_id].iloc[0]
        plan = generate_diet_plan(
            patient_id,
            patient['bmi'],
            patient['cholesterol'],
            patient['blood_sugar']
        )
        st.session_state.selected_patient = plan
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display plan
    if st.session_state.selected_patient:
        plan = st.session_state.selected_patient
        
        # Risk badge
        risk_class = f"risk-{plan['risk_level'].lower()}"
        st.markdown(f"""
            <div class="card">
                <h2>Patient: {plan['patient_id']}</h2>
                <span class="risk-badge {risk_class}">{plan['risk_level']} DIET RISK</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Diet plan details
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📅 7-Day Meal Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🌅 Breakfast:** {plan['breakfast']}")
            st.markdown(f"**🥗 Lunch:** {plan['lunch']}")
        
        with col2:
            st.markdown(f"**🍎 Snack:** {plan['snack']}")
            st.markdown(f"**🌙 Dinner:** {plan['dinner']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ANALYTICS PAGE
elif st.session_state.page == 'analytics':
    st.markdown("""
        <div class="main-header">
            <h1>📈 Health Analytics Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.patient_data is None:
        st.session_state.patient_data = generate_sample_data()
    
    df = st.session_state.patient_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BMI Distribution
        fig1 = px.histogram(df, x='bmi', nbins=20, 
                           title='BMI Distribution',
                           color_discrete_sequence=['#667eea'])
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Cholesterol vs Blood Sugar
        fig2 = px.scatter(df, x='cholesterol', y='blood_sugar',
                         size='bmi', color='age',
                         title='Cholesterol vs Blood Sugar',
                         color_continuous_scale='Viridis')
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Age distribution
    fig3 = px.box(df, y='age', title='Age Distribution',
                  color_discrete_sequence=['#764ba2'])
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    st.plotly_chart(fig3, use_container_width=True)

