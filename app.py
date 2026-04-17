import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# =========================
# כותרת
# =========================
st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# =========================
# נתונים
# =========================
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# =========================
# התראות
# =========================
st.markdown("<h4 style='text-align:right'>🚨 התראות</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    status = row["status"]

    color = "#e6ffe6" if status == "ירוק" else "#fff7e6" if status == "צהוב" else "#ffe5e5"

    st.markdown(f"""
    <div style="direction:rtl;text-align:right;padding:10px;margin-bottom:6px;
    border-radius:10px;border:1px solid #ddd;background:{color}">
    <b>{row['project_name']}</b><br>{status}
    </div>
    """, unsafe_allow_html=True)

# =========================
# Gemini
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# =========================
# AI אזור (פתרון יציב אמיתי)
# =========================
st.markdown("<h4 style='text-align:right'>🤖 אזור AI</h4>", unsafe_allow_html=True)

# הכל בשדה אחד (כדי לא לשבור layout)
project = st.selectbox("בחרי פרויקט", projects["project_name"].tolist())
question = st.text_area("שאלי שאלה / ניתוח")

run = st.button("הרצה")

if run:

    row = projects[projects["project_name"] == project].iloc[0]

    prompt = f"""
    נתונים:
    {projects.to_string(index=False)}

    פרויקט:
    {row['project_name']} - {row['status']}

    שאלה:
    {question}

    תשובה בעברית ברורה וקצרה
    """

    result = ask_gemini(prompt)

    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background: #fafafa;
        white-space: pre-wrap;
    ">
    {result}
    </div>
    """, unsafe_allow_html=True)
