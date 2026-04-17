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
# 🚨 התראות (כרטיסים RTL)
# =========================
st.markdown("<h4 style='text-align:right'>🚨 התראות</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    name = row["project_name"]
    status = row["status"]

    color = "#fafafa"
    border = "#ddd"

    if status == "אדום":
        color = "#ffe5e5"
        border = "#ff4d4d"
        icon = "⚠️"
    elif status == "צהוב":
        color = "#fff7e6"
        border = "#ffa500"
        icon = "⏳"
    else:
        icon = "✔"

    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 10px;
        border: 1px solid {border};
        background-color: {color};
        font-size: 15px;
    ">
    {icon} <b>{name}</b><br>
    סטטוס: {status}
    </div>
    """, unsafe_allow_html=True)

# =========================
# 📁 פרויקטים (כרטיסים)
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
        background-color: #ffffff;
        font-size: 15px;
    ">
    <b>פרויקט:</b> {row['project_name']}<br>
    <b>סטטוס:</b> {row['status']}
    </div>
    """, unsafe_allow_html=True)

# =========================
# 🤖 Gemini setup
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except:
        return "⚠️ עומס על המערכת – נסי שוב בעוד רגע"

# =========================
# 🎯 ניתוח פרויקט
# =========================
st.markdown("<h4 style='text-align:right'>🎯 ניתוח פרויקט</h4>", unsafe_allow_html=True)

project_names = projects["project_name"].tolist()
selected_project = st.selectbox("בחרי פרויקט", project_names)

if st.button("נתח פרויקט"):

    row = projects[projects["project_name"] == selected_project].iloc[0]

    prompt = f"""
    נתח את הפרויקט:

    שם: {row['project_name']}
    סטטוס: {row['status']}

    תן:
    - סיכון
    - בעיות
    - המלצה קצרה
    בעברית ברורה
    """

    result = ask_gemini(prompt)

    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #ccc;
        background-color: #f9f9f9;
        font-size: 15px;
        white-space: pre-wrap;
    ">
    {result}
    </div>
    """, unsafe_allow_html=True)

# =========================
# 💬 צ'אט חופשי עם AI
# =========================
st.markdown("<h4 style='text-align:right'>💬 שיחה חופשית עם AI</h4>", unsafe_allow_html=True)

user_question = st.text_area("שאלי שאלה על הפרויקטים")

if st.button("שלח ל-AI"):

    if user_question.strip():

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
            background-color: #ffffff;
            font-size: 15px;
            white-space: pre-wrap;
        ">
        {result}
        </div>
        """, unsafe_allow_html=True)
