import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# =========================
# פונקציית רווח אחיד
# =========================
def gap():
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# =========================
# כותרת ראשית
# =========================
st.markdown(
    "<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>",
    unsafe_allow_html=True
)

gap()

# =========================
# נתונים
# =========================
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# =========================
# 🚨 התראות
# =========================
st.markdown("<h4 style='text-align:right'>🚨 התראות</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    name = row["project_name"]
    status = row["status"]

    # ✔ חזרה לאייקונים המקוריים שלך
    if status == "אדום":
        color = "#ffe5e5"
        border = "#ff4d4d"
        icon = "⚠️"
        label = "פרויקט בסיכון"
        text_color = "#b30000"

    elif status == "צהוב":
        color = "#fff7e6"
        border = "#ffa500"
        icon = "⏳"
        label = "דורש מעקב"
        text_color = "#8a5a00"

    else:
        color = "#e6ffe6"
        border = "#2ecc71"
        icon = "✔"
        label = "תקין"
        text_color = "#1e7d32"

    st.markdown(f"""
    <div style="
        padding: 10px;
        margin-bottom: 6px;
        border-radius: 10px;
        border: 1px solid {border};
        background-color: {color};
        color: {text_color};
        direction: rtl;
        text-align: right;
    ">
        <b>{name}</b><br>
        {icon} {label}
    </div>
    """, unsafe_allow_html=True)

gap()

# =========================
# 📁 פרויקטים
# =========================
st.markdown("<h4 style='text-align:right'>📁 פרויקטים</h4>", unsafe_allow_html=True)

st.dataframe(projects, use_container_width=True)

gap()

# =========================
# 🤖 AI
# =========================
st.markdown("<h4 style='text-align:right'>🤖 אזור AI</h4>", unsafe_allow_html=True)

project_names = projects["project_name"].tolist()

selected_project = st.selectbox("בחרי פרויקט", project_names)
user_question = st.text_area("שאלה חופשית על הפרויקטים")

run = st.button("שלח ל-AI / נתח פרויקט")

gap()

# =========================
# Gemini setup
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "⚠️ שגיאה או עומס ב-Gemini"

# =========================
# 🤖 אזור AI
# =========================
st.markdown("<h4 style='text-align:right'>🤖 אזור AI</h4>", unsafe_allow_html=True)

project_names = projects["project_name"].tolist()

selected_project = st.selectbox("בחרי פרויקט לניתוח", project_names)

st.markdown("#### 🔎 ניתוח פרויקט")
analyze = st.button("נתח פרויקט")

st.markdown("---")

st.markdown("#### 💬 שאלה חופשית")

user_question = st.text_area("שאלי שאלה על כל הפרויקטים")

ask = st.button("שלח שאלה ל-AI")

# =========================
# Gemini setup
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "⚠️ שגיאה או עומס ב-Gemini"

# =========================
# ניתוח פרויקט
# =========================
if analyze:

    row = projects[projects["project_name"] == selected_project].iloc[0]

    prompt = f"""
נתח את הפרויקט הבא בצורה קצרה וברורה:

שם פרויקט: {row['project_name']}
סטטוס: {row['status']}

תן סיכום מצב והמלצה.
"""

    result = ask_gemini(prompt)

    st.markdown("### 🧠 ניתוח פרויקט")

    st.markdown(f"""
    <div style="
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background: #fafafa;
        direction: rtl;
        text-align: right;
        white-space: pre-wrap;
    ">
    {result}
    </div>
    """, unsafe_allow_html=True)

# =========================
# שאלה חופשית
# =========================
if ask:

    context = projects.to_string(index=False)

    prompt = f"""
את עוזרת לניהול פרויקטים.

נתונים:
{context}

שאלה כללית:
{user_question}

ענה בצורה קצרה וברורה בעברית.
"""

    result = ask_gemini(prompt)

    st.markdown("### 💬 תשובת AI")

    st.markdown(f"""
    <div style="
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background: #fafafa;
        direction: rtl;
        text-align: right;
        white-space: pre-wrap;
    ">
    {result}
    </div>
    """, unsafe_allow_html=True)
