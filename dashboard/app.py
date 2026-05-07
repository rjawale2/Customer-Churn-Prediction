import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---- PAGE SETTINGS ----
st.set_page_config(
    page_title="Customer Churn Dashboard",
    layout="wide"
)

# ---- LOAD DATA ----
# We load the original CSV to get real label names back
raw = pd.read_csv('dashboard/WA_Fn-UseC_-Telco-Customer-Churn.csv')
scored = pd.read_csv('dashboard/churn_scored.csv')

# Attach churn_probability and risk_tier from scored to raw
raw['churn_probability'] = scored['churn_probability']
raw['risk_tier'] = scored['risk_tier']
raw['Churn_Binary'] = raw['Churn'].map({'Yes': 1, 'No': 0})

df = raw.copy()

# ---- SIDEBAR FILTERS ----
st.sidebar.title("Filter Customers")

contract_options = df['Contract'].unique().tolist()
selected_contract = st.sidebar.multiselect(
    "Contract Type",
    options=contract_options,
    default=contract_options
)

internet_options = df['InternetService'].unique().tolist()
selected_internet = st.sidebar.multiselect(
    "Internet Service",
    options=internet_options,
    default=internet_options
)

risk_options = ['Low', 'Medium', 'High']
selected_risk = st.sidebar.multiselect(
    "Risk Tier",
    options=risk_options,
    default=risk_options
)

tenure_min, tenure_max = int(df['tenure'].min()), int(df['tenure'].max())
selected_tenure = st.sidebar.slider(
    "Tenure (months)",
    min_value=tenure_min,
    max_value=tenure_max,
    value=(tenure_min, tenure_max)
)

# ---- FILTER DATA ----
filtered_df = df[
    (df['Contract'].isin(selected_contract)) &
    (df['InternetService'].isin(selected_internet)) &
    (df['risk_tier'].isin(selected_risk)) &
    (df['tenure'] >= selected_tenure[0]) &
    (df['tenure'] <= selected_tenure[1])
]

# ---- TITLE ----
st.title("Customer Churn Intelligence Dashboard")
st.markdown("Track, analyze and understand customer churn patterns in real time.")
st.markdown("---")

# ---- KPI CARDS ----
st.markdown("### Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

total_customers = len(filtered_df)
churned = filtered_df['Churn_Binary'].sum()
churn_rate = round((churned / total_customers) * 100, 1) if total_customers > 0 else 0
high_risk_count = len(filtered_df[filtered_df['risk_tier'] == 'High'])
revenue_at_risk = round(
    filtered_df[filtered_df['risk_tier'] == 'High']['MonthlyCharges'].sum(), 2
)

col1.metric("👥 Total Customers", f"{total_customers:,}")
col2.metric("🚨 Churned", f"{churned:,}")
col3.metric("📉 Churn Rate", f"{churn_rate}%")
col4.metric("🔴 High Risk", f"{high_risk_count:,}")
col5.metric("💰 Revenue at Risk", f"${revenue_at_risk:,.0f}/mo")

st.markdown("---")

# ---- ROW 1: Contract churn + Risk pie ----
st.markdown("### 📈 Churn Overview")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("#### Churn Rate by Contract")
    contract_churn = filtered_df.groupby('Contract')['Churn_Binary'].mean().reset_index()
    contract_churn['Churn Rate (%)'] = (contract_churn['Churn_Binary'] * 100).round(1)
    fig1 = px.bar(
        contract_churn,
        x='Contract', y='Churn Rate (%)',
        color='Churn Rate (%)',
        color_continuous_scale='Reds',
        text='Churn Rate (%)'
    )
    fig1.update_traces(texttemplate='%{text}%', textposition='outside')
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.markdown("#### Risk Tier Breakdown")
    risk_counts = filtered_df['risk_tier'].value_counts().reset_index()
    risk_counts.columns = ['Risk Tier', 'Count']
    fig2 = px.pie(
        risk_counts,
        names='Risk Tier',
        values='Count',
        color='Risk Tier',
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f39c12',
            'High': '#e74c3c'
        },
        hole=0.4
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_c:
    st.markdown("#### Churn by Internet Service")
    internet_churn = filtered_df.groupby('InternetService')['Churn_Binary'].mean().reset_index()
    internet_churn['Churn Rate (%)'] = (internet_churn['Churn_Binary'] * 100).round(1)
    fig3 = px.bar(
        internet_churn,
        x='InternetService', y='Churn Rate (%)',
        color='Churn Rate (%)',
        color_continuous_scale='Blues',
        text='Churn Rate (%)'
    )
    fig3.update_traces(texttemplate='%{text}%', textposition='outside')
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---- ROW 2: Tenure + Monthly Charges ----
st.markdown("### 💡 Customer Behavior Insights")
col_d, col_e = st.columns(2)

with col_d:
    st.markdown("#### Churn Rate by Tenure Group")
    df_tenure = filtered_df.copy()
    df_tenure['Tenure Group'] = pd.cut(
        df_tenure['tenure'],
        bins=[0, 6, 12, 24, 48, 72],
        labels=['0-6 mo', '6-12 mo', '12-24 mo', '24-48 mo', '48-72 mo']
    )
    tenure_churn = df_tenure.groupby('Tenure Group', observed=True)['Churn_Binary'].mean().reset_index()
    tenure_churn['Churn Rate (%)'] = (tenure_churn['Churn_Binary'] * 100).round(1)
    fig4 = px.line(
        tenure_churn,
        x='Tenure Group', y='Churn Rate (%)',
        markers=True,
        line_shape='spline',
        color_discrete_sequence=['#e74c3c']
    )
    st.plotly_chart(fig4, use_container_width=True)

with col_e:
    st.markdown("#### Monthly Charges vs Churn Probability")
    fig5 = px.scatter(
        filtered_df,
        x='MonthlyCharges',
        y='churn_probability',
        color='risk_tier',
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f39c12',
            'High': '#e74c3c'
        },
        opacity=0.5,
        labels={'churn_probability': 'Churn Probability'}
    )
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ---- ROW 3: Payment method + Senior Citizens ----
st.markdown("### 🔎 Segment Deep Dives")
col_f, col_g = st.columns(2)

with col_f:
    st.markdown("#### Churn by Payment Method")
    payment_churn = filtered_df.groupby('PaymentMethod')['Churn_Binary'].mean().reset_index()
    payment_churn['Churn Rate (%)'] = (payment_churn['Churn_Binary'] * 100).round(1)
    fig6 = px.bar(
        payment_churn.sort_values('Churn Rate (%)', ascending=True),
        x='Churn Rate (%)', y='PaymentMethod',
        orientation='h',
        color='Churn Rate (%)',
        color_continuous_scale='Oranges',
        text='Churn Rate (%)'
    )
    fig6.update_traces(texttemplate='%{text}%', textposition='outside')
    fig6.update_layout(showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

with col_g:
    st.markdown("#### Senior Citizens vs Non-Senior Churn")
    filtered_df['Customer Type'] = filtered_df['SeniorCitizen'].map(
        {0: 'Non-Senior', 1: 'Senior Citizen'}
    )
    senior_churn = filtered_df.groupby('Customer Type')['Churn_Binary'].mean().reset_index()
    senior_churn['Churn Rate (%)'] = (senior_churn['Churn_Binary'] * 100).round(1)
    fig7 = px.bar(
        senior_churn,
        x='Customer Type', y='Churn Rate (%)',
        color='Customer Type',
        color_discrete_sequence=['#3498db', '#e74c3c'],
        text='Churn Rate (%)'
    )
    fig7.update_traces(texttemplate='%{text}%', textposition='outside')
    fig7.update_layout(showlegend=False)
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# ---- ROW 4: Churn probability distribution + Heatmap ----
st.markdown("### 📊 Advanced Analytics")
col_h, col_i = st.columns(2)

with col_h:
    st.markdown("#### Churn Probability Distribution")
    fig8 = px.histogram(
        filtered_df,
        x='churn_probability',
        color='risk_tier',
        nbins=40,
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f39c12',
            'High': '#e74c3c'
        },
        labels={'churn_probability': 'Churn Probability'}
    )
    st.plotly_chart(fig8, use_container_width=True)

with col_i:
    st.markdown("#### Avg Monthly Charges by Contract & Internet")
    heatmap_data = filtered_df.groupby(
        ['Contract', 'InternetService']
    )['MonthlyCharges'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(
        index='Contract', columns='InternetService', values='MonthlyCharges'
    )
    fig9 = px.imshow(
        heatmap_pivot,
        color_continuous_scale='RdYlGn_r',
        text_auto='.0f',
        labels={'color': 'Avg Monthly Charge ($)'}
    )
    st.plotly_chart(fig9, use_container_width=True)

st.markdown("---")

# ---- HIGH RISK TABLE ----
st.markdown("### 🔴 High Risk Customers")
high_risk = filtered_df[filtered_df['risk_tier'] == 'High'][[
    'gender', 'SeniorCitizen', 'tenure', 'Contract',
    'InternetService', 'MonthlyCharges', 'TotalCharges',
    'PaymentMethod', 'churn_probability', 'risk_tier'
]].sort_values('churn_probability', ascending=False).reset_index(drop=True)

st.dataframe(high_risk, use_container_width=True)
st.caption(f"Showing {len(high_risk)} high risk customers")
st.markdown("---")

# ---- CUSTOMER CHURN PREDICTOR ----
st.markdown("### 🔮 Predict Churn for a New Customer")
st.markdown("Fill in the customer details below and we will predict their churn risk.")

import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Load model
with open('dashboard/churn_model.pkl', 'rb') as f:
    model = pickle.load(f)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 👤 Personal Info")
    gender = st.selectbox("Gender", ["Male", "Female"])
    senior = st.selectbox("Senior Citizen", ["No", "Yes"])
    partner = st.selectbox("Has Partner", ["Yes", "No"])
    dependents = st.selectbox("Has Dependents", ["Yes", "No"])
    tenure = st.slider("Tenure (months)", 0, 72, 12)

with col2:
    st.markdown("#### 📱 Services")
    phone_service = st.selectbox("Phone Service", ["Yes", "No"])
    multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
    online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
    device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
    tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
    streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
    streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])

with col3:
    st.markdown("#### 💳 Billing")
    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    paperless = st.selectbox("Paperless Billing", ["Yes", "No"])
    payment = st.selectbox("Payment Method", [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ])
    monthly_charges = st.number_input("Monthly Charges ($)", 0.0, 200.0, 65.0)
    total_charges = st.number_input("Total Charges ($)", 0.0, 10000.0, monthly_charges * tenure)

# ---- PREDICT BUTTON ----
if st.button("🔮 Predict Churn Risk", use_container_width=True):

    # Encode inputs exactly like your notebook did
    input_data = {
        'gender': 1 if gender == 'Male' else 0,
        'SeniorCitizen': 1 if senior == 'Yes' else 0,
        'Partner': 1 if partner == 'Yes' else 0,
        'Dependents': 1 if dependents == 'Yes' else 0,
        'tenure': tenure,
        'PhoneService': 1 if phone_service == 'Yes' else 0,
        'MultipleLines': {'No phone service': 0, 'No': 1, 'Yes': 2}[multiple_lines],
        'InternetService': {'DSL': 0, 'Fiber optic': 1, 'No': 2}[internet_service],
        'OnlineSecurity': {'No internet service': 0, 'No': 1, 'Yes': 2}[online_security],
        'OnlineBackup': {'No internet service': 0, 'No': 1, 'Yes': 2}[online_backup],
        'DeviceProtection': {'No internet service': 0, 'No': 1, 'Yes': 2}[device_protection],
        'TechSupport': {'No internet service': 0, 'No': 1, 'Yes': 2}[tech_support],
        'StreamingTV': {'No internet service': 0, 'No': 1, 'Yes': 2}[streaming_tv],
        'StreamingMovies': {'No internet service': 0, 'No': 1, 'Yes': 2}[streaming_movies],
        'Contract': {'Month-to-month': 0, 'One year': 1, 'Two year': 2}[contract],
        'PaperlessBilling': 1 if paperless == 'Yes' else 0,
        'PaymentMethod': {
            'Bank transfer (automatic)': 0,
            'Credit card (automatic)': 1,
            'Electronic check': 2,
            'Mailed check': 3
        }[payment],
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges
    }

    input_df = pd.DataFrame([input_data])

    # Predict
    churn_prob = model.predict_proba(input_df)[0][1]
    churn_percent = round(churn_prob * 100, 1)

    # Risk tier
    if churn_prob >= 0.65:
        risk = "🔴 HIGH RISK"
        color = "red"
    elif churn_prob >= 0.35:
        risk = "🟡 MEDIUM RISK"
        color = "orange"
    else:
        risk = "🟢 LOW RISK"
        color = "green"

    # ---- RESULT ----
    st.markdown("---")
    st.markdown(f"## Prediction Result: {risk}")

    # Progress bar
    st.markdown(f"### Churn Probability: {churn_percent}%")
    st.progress(churn_prob)

    # ---- SMART EXPLANATIONS ----
    st.markdown("### ⚠️ Risk Factors Detected")
    reasons = []
    recommendations = []

    if contract == "Month-to-month":
        reasons.append("📋 Month-to-month contract — highest churn risk contract type")
        recommendations.append("💡 Offer incentive to upgrade to a 1 or 2 year contract")

    if tenure < 6:
        reasons.append(f"🕐 Very new customer ({tenure} months) — early churn window")
        recommendations.append("💡 Assign onboarding support for first 90 days")

    if internet_service == "Fiber optic" and online_security == "No":
        reasons.append("🔒 Fiber optic with no online security — common churn pattern")
        recommendations.append("💡 Offer free 3-month online security trial")

    if monthly_charges > 70 and contract == "Month-to-month":
        reasons.append(f"💸 High monthly charges (${monthly_charges}) with no long term commitment")
        recommendations.append("💡 Offer bundled discount to reduce monthly cost")

    if senior == "Yes" and tech_support == "No":
        reasons.append("👴 Senior citizen with no tech support — vulnerable segment")
        recommendations.append("💡 Offer dedicated senior support plan")

    if payment == "Electronic check":
        reasons.append("💳 Electronic check users have highest churn rates")
        recommendations.append("💡 Encourage switch to automatic payment method")

    if paperless == "Yes" and contract == "Month-to-month":
        reasons.append("📧 Paperless billing + month-to-month is a high churn combo")

    if len(reasons) == 0:
        reasons.append("✅ No major risk factors detected for this customer")

    for r in reasons:
        st.markdown(f"- {r}")

    st.markdown("### 💡 Retention Recommendations")
    if len(recommendations) == 0:
        st.markdown("- ✅ Customer appears stable. Continue regular engagement.")
    else:
        for rec in recommendations:
            st.markdown(f"- {rec}")