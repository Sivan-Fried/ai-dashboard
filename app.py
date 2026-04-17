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
# 👤 תמונת פרופיל (תיקון: PNG)
# =========================
import os

img_path = os.path.join(os.path.dirname(__file__), "profile.png")
st.markdown("""
<div style="
    display: flex;
    justify-content: center;
    margin-top: 10px;
    margin-bottom: 10px;
">
    <img src="profile.png" style="
        width:140px;
        height:140px;
        border-radius:50%;
        object-fit: cover;
        border: 3px solid #ddd;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.15);
    ">
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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

st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# 📁 פרויקטים
# =========================
st.markdown("<h4 style='text-align:right'>📁 פרויקטים</h4>", unsafe_allow_html=True)

st.dataframe(projects, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# 🤖 AI
# =========================
st.markdown("<h4 style='text-align:right'>🤖 אזור AI</h4>", unsafe_allow_html=True)

project_names = projects["project_name"].tolist()

selected_project = st.selectbox("בחרי פרויקט", project_names)
user_question = st.text_area("שאלה חופשית על הפרויקטים")

run = st.button("שלח ל-AI / נתח פרויקט")

# =========================
# Gemini setup
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ שגיאה: {e}"

# =========================
# הרצת AI
# =========================
if run:

    filtered = projects[projects["project_name"] == selected_project]

    if filtered.empty:
        st.error("לא נמצא פרויקט")
    else:
        row = filtered.iloc[0]

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
