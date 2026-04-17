import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

st.markdown(
    "<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>",
    unsafe_allow_html=True
)

projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# ===== התראות =====
st.markdown("<h4 style='text-align:right'>🚨 התראות</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    name = row["project_name"]
    status = row["status"]

    color = "#e6ffe6" if status == "ירוק" or status == "תקין" else "#fff7e6" if status == "צהוב" else "#ffe5e5"

    st.markdown(f"""
    <div style="direction:rtl; text-align:right; padding:10px; margin-bottom:6px;
    border-radius:10px; border:1px solid #ddd; background:{color}">
    <b>{name}</b><br>
    סטטוס: {status}
    </div>
    """, unsafe_allow_html=True)

# ===== Gemini =====
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# =========================
# 💬 אזור AI (ימין אמיתי)
# =========================

st.markdown("<h4 style='text-align:right'>💬 שיחה חופשית עם AI</h4>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])  # col2 = ימני (עיקרי)

with col2:
    user_question = st.text_area("שאלי שאלה על הפרויקטים")

    if st.button("שלח ל-AI"):

        context = projects.to_string(index=False)

        prompt = f"""
        את עוזרת לניהול פרויקטים.

        נתונים:
        {context}

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
            background-color: #fafafa;
            white-space: pre-wrap;
        ">
        {result}
        </div>
        """, unsafe_allow_html=True)
            white-space: pre-wrap;
        ">
        {result}
        </div>
        """, unsafe_allow_html=True)
