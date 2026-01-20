# AI-ML-based-Personalized-Diet-Plan-Generator-from-Medical-Report
🏥 AI Medical Diet Plan Generator

An AI-powered Streamlit web application that analyzes medical reports (PDFs), extracts key health metrics, and generates personalized diet plans, nutrition guidelines, and lifestyle recommendations. The system also allows users to download structured reports in PDF and JSON formats.

📌 Project Overview

Medical reports often contain complex and unstructured health data that is difficult for patients to interpret. This application automates the process by:

Extracting health metrics from uploaded medical PDF reports

Analyzing health conditions using rule-based logic

Generating personalized diet and lifestyle recommendations

Providing downloadable reports for easy sharing with healthcare professionals

🎯 Key Features

📄 PDF Medical Report Upload

🔍 Automatic Health Metric Extraction

BMI

Blood Sugar

Blood Pressure

Cholesterol

Hemoglobin

HDL / LDL / Triglycerides

🩺 Health Status Assessment (Normal / High / Low)

🍽️ Personalized Diet Plan

Breakfast, Lunch, Dinner, Snacks

📊 Daily Nutrition Targets

💪 Lifestyle & Exercise Recommendations

📑 Download Reports

JSON (structured data)

PDF (formatted medical diet plan)

🎨 Professional UI with Custom Styling

⚠️ Medical Disclaimer Included

🛠️ Technologies Used

Python

Streamlit – Web UI

PyPDF2 – PDF text extraction

Regex (re) – Health metric parsing

ReportLab – PDF report generation

JSON – Data export

🧩 Application Workflow

User uploads a medical report (PDF)

System extracts text from the PDF

Health metrics are detected using regex patterns

Health conditions are identified

Personalized:

Diet Plan

Nutrition Guidelines

Lifestyle Recommendations

User downloads the report in PDF or JSON

📂 Project Structure
AI-Medical-Diet-Plan-Generator/
│
├── app.py                 # Main Streamlit application
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies

📥 Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/AI-Medical-Diet-Plan-Generator.git
cd AI-Medical-Diet-Plan-Generator

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Run the Application
streamlit run app.py

📦 Required Libraries

Add this to your requirements.txt:

streamlit
PyPDF2
reportlab

🧪 Sample Medical Report Requirements

Your PDF should contain standard fields such as:

Name

Age

Gender

BMI

Blood Sugar

Blood Pressure

Cholesterol

Hemoglobin

The system uses pattern matching, so clearer lab formats give better results.

⚠️ Disclaimer

This application provides general dietary guidance only.
It is not a substitute for professional medical advice.
Always consult a certified doctor or nutritionist before making health decisions.

🚀 Future Enhancements

OCR support for scanned medical reports

ML-based disease prediction

Doctor / patient dashboard

Cloud deployment (AWS / Streamlit Cloud)

Multi-language support

AI chatbot for diet guidance
