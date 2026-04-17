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
# התראות (נקי ויציב)
# =========================
st.markdown("### 🚨 התראות")

for _, row in projects.iterrows():
    status = row["status"]
    name = row["project_name"]

    if status == "אדום":
        bg = "#ffe5e5"
        icon = "⚠️"
    elif status == "צהוב":
        bg = "#fff7e6"
        icon = "⏳"
    else:
        bg = "#e6ffe6"
        icon = "✔"

    st.markdown(
        f"""
        <div style="
            padding:10px;
            margin-bottom:6px;
            border-radius:10px;
            background:{bg};
            border:1px solid #ddd;
            direction:rtl;
            text-align:right;
        ">
        {icon} <b>{name}</b><br>
        סטטוס: {status}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# =========================
# פרויקטים
# =========================
st.markdown("### 📁 פרויקטים")

st.dataframe(projects, use_container_width=True)

st.markdown("---")

# =========================
# Gemini
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except:
        return "שגיאה או עומס ב-Gemini"

# =========================
# AI אזור (מסודר ולא שבור)
# =========================
st.markdown("### 🤖 אזור AI")

# בלוק אחד ברור (ללא פיצול מבלבל)
project_names = projects["project_name"].tolist()

selected_project = st.selectbox("בחרי פרויקט", project_names)
question = st.text_area("שאלה חופשית / ניתוח פרויקט")

run = st.button("שלח ל-AI")

# =========================
# הרצה
# =========================
if run:

    row = projects[projects["project_name"] == selected_project].iloc[0]

    context = projects.to_string(index=False)

    prompt = f"""
    את עוזרת לניהול פרויקטים.

    נתונים:
    {context}

    פרויקט נבחר:
    {row['project_name']} - {row['status']}

    שאלה:
    {question}

    תני תשובה קצרה וברורה בעברית.
    """

    result = ask_gemini(prompt)

    st.markdown("### 🧠 תשובת AI")

    st.markdown(
        f"""
        <div style="
            direction:rtl;
            text-align:right;
            padding:14px;
            border-radius:10px;
            background:#fafafa;
            border:1px solid #ddd;
            white-space:pre-wrap;
        ">
        {result}
        </div>
        """,
        unsafe_allow_html=True
    )
