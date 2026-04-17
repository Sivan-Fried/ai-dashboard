import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# ===== כותרת =====
st.markdown(
    "<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>",
    unsafe_allow_html=True
)

# ===== נתונים =====
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# =========================
# 🚨 התראות
# =========================
st.markdown("<h4 style='text-align:right'>🚨 התראות</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    status = row["status"]
    name = row["project_name"]

    if status == "אדום":
        color = "#ffe5e5"
        border = "#ff4d4d"
        icon = "⚠️"
    elif status == "צהוב":
        color = "#fff7e6"
        border = "#ffa500"
        icon = "⏳"
    else:
        color = "#e6ffe6"
        border = "#2ecc71"
        icon = "✔"

    st.markdown(f"""
    <div style="direction:rtl;text-align:right;padding:10px;
    margin-bottom:8px;border-radius:10px;border:1px solid {border};
    background:{color}">
    {icon} <b>{name}</b><br>
    סטטוס: {status}
    </div>
    """, unsafe_allow_html=True)

# =========================
# מרווח
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# ===== AI AREA (מבודד לימין) =====
# =========================
st.markdown("<div style='text-align:right'><h4>🤖 אזור AI</h4></div>", unsafe_allow_html=True)

right, left = st.columns([2, 1])

with right:

    project_names = projects["project_name"].tolist()
    selected_project = st.selectbox("בחרי פרויקט", project_names)

    user_question = st.text_area("שאלי שאלה על הפרויקטים")

    run = st.button("שלח ל-AI / נתח פרויקט")

# ===== Gemini =====
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# =========================
# פעולה
# =========================
if run:

    context = projects.to_string(index=False)

    row = projects[projects["project_name"] == selected_project].iloc[0]

    prompt = f"""
    נתונים:
    {context}

    פרויקט נבחר:
    {row['project_name']} - {row['status']}

    שאלה:
    {user_question}

    תן תשובה בעברית קצרה וברורה
    """

    result = ask_gemini(prompt)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #ddd;
        background: #fafafa;
        white-space: pre-wrap;
    ">
    {result}
    </div>
    """, unsafe_allow_html=True)
