# 📊 Customer Churn Prediction & Analytics Dashboard

## 🔍 Project Overview
This project analyzes customer churn for a telecom company using 
machine learning and presents the findings through an interactive 
business intelligence dashboard.

## 🎯 Objective
To predict which customers are likely to churn and provide 
actionable retention recommendations to reduce customer loss.

## 📁 Project Structure
- **notebook/** — Exploratory data analysis and model building
- **dashboard/** — Interactive Streamlit dashboard

## 🛠️ Tools & Technologies
- Python, Pandas, NumPy
- Scikit-learn (Random Forest)
- Streamlit, Plotly
- Google Colab

## 📊 Dashboard Features
- KPI metrics (churn rate, revenue at risk)
- 8 interactive charts
- Customer segment filters
- New customer churn predictor
- Smart risk explanations & retention recommendations

## 🤖 Model Performance
- Algorithm: Random Forest Classifier
- ROC-AUC Score: 0.86
- Churn Recall: 0.87 (at threshold 0.35)

## 📦 How to Run
1. Clone this repository
2. Install dependencies
\```
pip install -r requirements.txt
\```
3. Run the dashboard
\```
streamlit run dashboard/app.py
\```

## 📈 Dataset
IBM Telco Customer Churn Dataset — 7,043 customers, 21 features

## 👤 Author
Your Name Here
