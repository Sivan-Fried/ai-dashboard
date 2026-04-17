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

# ===== התראות =====
st.markdown("<h4 style='text-align:right'>🚨 התראות</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    name = row["project_name"]
    status = row["status"]

    if status == "אדום":
        st.error(f"⚠️ {name}")
    elif status == "צהוב":
        st.warning(f"⏳ {name}")
    else:
        st.success(f"✔ {name}")

# ===== פרויקטים (כרטיסים בלבד - RTL אמיתי) =====
st.markdown("<h4 style='text-align:right'>📁 פרויקטים</h4>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 14px;
        border: 1px solid #ddd;
        border-radius: 12px;
        margin-bottom: 10px;
        background-color: #fafafa;
        font-size: 15px;
    ">
        <b>פרויקט:</b> {row['project_name']}<br>
        <b>סטטוס:</b> {row['status']}
    </div>
    """, unsafe_allow_html=True)

# ===== Gemini =====
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# ===== ניתוח פרויקט =====
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
    בעברית
    """

    result = ask_gemini(prompt)

    st.markdown(f"""
    <div style="
        direction: rtl;
        text-align: right;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid #ddd;
        background-color: white;
    ">
    {result}
    </div>
    """, unsafe_allow_html=True)

# ===== צ'אט חופשי =====
st.markdown("<h4 style='text-align:right'>💬 שיחה חופשית עם AI</h4>", unsafe_allow_html=True)

user_question = st.text_area("שאלי שאלה")

if st.button("שלח ל-AI"):

    if user_question.strip():

        context = projects.to_string(index=False)

        prompt = f"""
        את עוזרת לניהול פרויקטים.

        נתונים:
        {context}

        שאלה:
        {user_question}

        תשובה בעברית קצרה וברורה
        """

        result = ask_gemini(prompt)

        st.markdown(f"""
        <div style="
            direction: rtl;
            text-align: right;
            padding: 14px;
            border-radius: 12px;
            border: 1px solid #ddd;
            background-color: #fafafa;
        ">
        {result}
        </div>
        """, unsafe_allow_html=True)
