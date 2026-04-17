import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# =========================
# כותרת
# =========================
st.markdown(
    "<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>",
    unsafe_allow_html=True
)

# =========================
# נתונים
# =========================
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# =========================
# 🚨 התראות (חזר!)
# =========================
st.markdown("<h4 style='text-align:right'>🚨 התראות</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    name = row["project_name"]
    status = row["status"]

    if status == "אדום":
        color = "#ffe5e5"
        border = "#ff4d4d"
        icon = "⚠️"
        text_color = "#b30000"

    elif status == "צהוב":
        color = "#fff7e6"
        border = "#ffa500"
        icon = "⏳"
        text_color = "#8a5a00"

    else:
        color = "#e6ffe6"
        border = "#2ecc71"
        icon = "✔"
        text_color = "#1e7d32"

    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 10px;
        border: 1px solid {border};
        background-color: {color};
        color: {text_color};
    ">
    {icon} <b>{name}</b><br>
    סטטוס: {status}
    </div>
    """, unsafe_allow_html=True)

# =========================
# רווח
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# 📁 פרויקטים
# =========================
st.markdown("<h4 style='text-align:right'>📁 פרויקטים</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background: #ffffff;
    ">
    <b>פרויקט:</b> {row['project_name']}<br>
    <b>סטטוס:</b> {row['status']}
    </div>
    """, unsafe_allow_html=True)

# =========================
# Gemini
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except:
        return "⚠️ שגיאה / עומס על Gemini"

# =========================
# 🤖 AI אזור
# =========================
st.markdown("<br><h4 style='text-align:right'>🤖 אזור AI</h4>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:

    project_names = projects["project_name"].tolist()
    selected_project = st.selectbox("בחרי פרויקט", project_names)

    user_question = st.text_area("שאלי שאלה על הפרויקטים")

    run = st.button("שלח ל-AI / נתח")

# =========================
# הרצת AI
# =========================
if run:

    row = projects[projects["project_name"] == selected_project].iloc[0]
    context = projects.to_string(index=False)

    prompt = f"""
    את עוזרת לניהול פרויקטים.

    כל הנתונים:
    {context}

    פרויקט נבחר:
    {row['project_name']} - {row['status']}

    שאלה:
    {user_question}

    תשובה קצרה וברורה בעברית
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
