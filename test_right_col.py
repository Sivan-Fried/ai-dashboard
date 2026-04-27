import streamlit as st
import urllib.parse
import pandas as pd
import datetime

# דמה של נתונים
projects = pd.DataFrame([
    {"project_name": "AnalystCustomers", "project_type": "אנליזה", "status": "ירוק"},
    {"project_name": "IDI App", "project_type": "פיתוח", "status": "צהוב"},
])
priority_df = pd.DataFrame([
    {"project_name": "אנליסט פרויקט A", "project_number": "P-001", "order_number": "O-11"},
    {"project_name": "דנאל פרויקט B", "project_number": "P-002", "order_number": "O-22"},
])
meetings = pd.DataFrame([])
today = datetime.date.today()

# הגדרת עמוד
st.set_page_config(layout="wide")

# ⭐ CSS מלא שמייצר את הכרטיס הוורוד כמו בתמונה ⭐
st.markdown("""
<style>
.ai-card {
    background-color: #FADCE6;
    padding: 24px;
    border-radius: 24px;
    box-shadow: 0px 10px 30px rgba(225,200,210,0.25);
    direction: rtl;
    margin-bottom: 20px;
    width: 100%;
}

.ai-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.ai-header h4 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #6f5861;
}

.ai-description {
    font-size: 14px;
    color: #6f5861;
    opacity: 0.85;
    margin-bottom: 20px;
    text-align: right;
}

.ai-send-btn {
    position: absolute;
    left: 12px;
    bottom: 12px;
    width
