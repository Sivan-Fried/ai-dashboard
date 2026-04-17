import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# =========================
# RTL גלובלי (חשוב מאוד)
# =========================
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# =========================
# כותרת ראשית
# =========================
st.markdown("## 📊 Dashboard AI לניהול פרויקטים")

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# נתונים
# =========================
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# =========================
# 🚨 התראות
# =========================
st.markdown("### 🚨 התראות")

for _, row in projects.iterrows():
    name = row["project_name"]
    status = row["status"]

    if status == "אדום":
        color = "#ffe5e5"
        border = "#ff4d4d"
        icon = "⚠️"
        text_color = "#b30000"
        label = "פרויקט בסיכון"

    elif status == "צהוב":
        color = "#fff7e6"
        border = "#ffa500"
        icon = "⏳"
        text_color = "#8a5a00"
        label = "דורש מעקב"

    else:
        color = "#e6ffe6"
        border = "#2ecc71"
        icon = "✔"
        text_color = "#1e7d32"
        label = "תקין"

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

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# 📁 פרויקטים
# =========================
st.markdown("### 📁 פרויקטים")

st.dataframe(projects, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# 🤖 AI
# =========================
st.markdown("### 🤖 אזור AI")

project_names = projects["project_name"].tolist()

selected_project = st.selectbox("בחרי פרויקט", project_names)
user_question = st.text_area("שאלה על הפרויקטים")

run = st.button("שלח ל-AI / נתח פרויקט")

# =========================
# Gemini
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except:
        return "⚠️ שגיאה או עומס ב-Gemini"

# =========================
# תוצאה
# =========================
if run:

    row = projects[projects["project_name"] == selected_project].iloc[0]

    context = projects.to_string(index=False)

    prompt = f"""
    את עוזרת לניהול פרויקטים.

    נתונים:
    {context}

    פרויקט:
    {row['project_name']} - {row['status']}

    שאלה:
    {user_question}

    תשובה קצרה וברורה בעברית
    """

    result = ask_gemini(prompt)

    st.markdown("### 🧠 תשובת AI")

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
