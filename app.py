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
# Gemini
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# =========================
# מבנה עמוד קבוע (חשוב ליציבות)
# =========================
top, middle, bottom = st.columns(3)

# =========================
# התראות
# =========================
with top:
    st.markdown("### 🚨 התראות")

    for _, row in projects.iterrows():
        status = row["status"]

        color = "#e6ffe6" if status == "ירוק" else "#fff7e6" if status == "צהוב" else "#ffe5e5"

        st.markdown(f"""
        <div style="padding:10px;margin-bottom:6px;border-radius:8px;
        background:{color};border:1px solid #ddd;text-align:right;direction:rtl">
        <b>{row['project_name']}</b><br>{status}
        </div>
        """, unsafe_allow_html=True)

# =========================
# פרויקטים
# =========================
with middle:
    st.markdown("### 📁 פרויקטים")
    st.dataframe(projects, use_container_width=True)

# =========================
# AI
# =========================
with bottom:
    st.markdown("### 🤖 אזור AI")

    project = st.selectbox("בחרי פרויקט", projects["project_name"].tolist())
    question = st.text_area("שאלה חופשית")

    run = st.button("שלח")

    if run:
        row = projects[projects["project_name"] == project].iloc[0]

        prompt = f"""
        נתונים:
        {projects.to_string(index=False)}

        פרויקט:
        {row['project_name']} - {row['status']}

        שאלה:
        {question}
        """

        result = ask_gemini(prompt)

        st.markdown(f"""
        <div style="
            direction:rtl;
            text-align:right;
            padding:12px;
            border-radius:10px;
            background:#fafafa;
            border:1px solid #ddd;
            white-space:pre-wrap;
        ">
        {result}
        </div>
        """, unsafe_allow_html=True)
        {result}
        </div>
        """,
        unsafe_allow_html=True
    )
