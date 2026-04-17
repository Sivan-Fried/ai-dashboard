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
# נתונים (חשוב שיהיה כאן)
# =========================
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# =========================
# פרויקטים (חייב להיות ראשון כדי שלא "ייעלם")
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
# רווח
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# Gemini
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# =========================
# אזור AI (מסודר)
# =========================
st.markdown("<h4 style='text-align:right'>🤖 אזור AI</h4>", unsafe_allow_html=True)

col_right, col_left = st.columns([2, 1])

with col_right:

    project_names = projects["project_name"].tolist()
    selected_project = st.selectbox("בחרי פרויקט", project_names)

    user_question = st.text_area("שאלי שאלה על הפרויקטים")

    run = st.button("שלח ל-AI / נתח")

# =========================
# הרצה
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
