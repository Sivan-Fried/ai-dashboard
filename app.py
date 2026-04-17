import streamlit as st
import pandas as pd
import os
import base64
import google.generativeai as genai

st.set_page_config(layout="wide")

# =========================
# עיצוב בסיס
# =========================
st.markdown("""
<style>
body {
    background-color: #f6f7fb;
}

.card {
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-bottom: 8px;
    background: white;
    direction: rtl;
    text-align: right;
}

h1, h2, h3, h4 {
    color: #1f2a44;
}
</style>
""", unsafe_allow_html=True)

# =========================
# כותרת
# =========================
st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# =========================
# תמונת פרופיל
# =========================
def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("profile.png")

st.markdown(f"""
<div style="display:flex; justify-content:center; margin:10px 0;">
    <div style="
        width:120px;
        height:120px;
        border-radius:50%;
        overflow:hidden;
        border:3px solid #ddd;
        box-shadow:0 2px 10px rgba(0,0,0,0.15);
    ">
        <img src="data:image/png;base64,{img_base64}" style="
            width:100%;
            height:100%;
            object-fit:cover;
            object-position:center top;
        ">
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# נתונים
# =========================
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")
meetings = pd.read_excel("meetings.xlsx", engine="openpyxl")

# =========================
# KPI
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<div class='card'><b>סה״כ פרויקטים</b><br>{len(projects)}</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='card'><b>בסיכון 🔴</b><br>{len(projects[projects['status']=='אדום'])}</div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='card'><b>במעקב 🟡</b><br>{len(projects[projects['status']=='צהוב'])}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# פריסה מרכזית
# =========================
col_left, col_right = st.columns([1, 2])

# -------- התראות --------
with col_left:
    st.markdown("### 🚨 התראות")

    for _, row in projects.iterrows():
        status = row["status"]
        name = row["project_name"]

        if status == "אדום":
            icon = "🔴"
            label = "פרויקט בסיכון"
        elif status == "צהוב":
            icon = "🟡"
            label = "דורש מעקב"
        else:
            icon = "🟢"
            label = "תקין"

        st.markdown(f"""
        <div class="card">
            {icon} <b>{label}</b><br>
            {name}
        </div>
        """, unsafe_allow_html=True)

# -------- פרויקטים --------
with col_right:
    st.markdown("### 📁 פרויקטים")
    st.dataframe(projects, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =========================
# פגישות היום
# =========================
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("### 📅 הפגישות שלי היום")

today = pd.Timestamp.today().date()
today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]

if today_meetings.empty:
    st.info("אין פגישות היום 🎉")
else:
    meetings_html = ""

    for _, row in today_meetings.iterrows():
        meetings_html += f"""
        <div style="
            padding:10px;
            border-bottom:1px solid #eee;
            direction:rtl;
            text-align:right;
        ">
            📌 <b>{row['meeting_title']}</b>
            &nbsp; | 🕒 {row['time']}
            &nbsp; | 📁 {row['project_name']}
            &nbsp; | 👤 {row['owner']}
            &nbsp; | 📊 {row['status']}
        </div>
        """

    st.markdown(f"""
    <div style="
        background:white;
        padding:15px;
        border-radius:12px;
        box-shadow:0 2px 10px rgba(0,0,0,0.08);
        direction:rtl;
        text-align:right;
    ">
        {meetings_html}
    </div>
    """, unsafe_allow_html=True)

# =========================
# AI
# =========================
st.markdown("### 🤖 אזור AI")

project_names = projects["project_name"].tolist()

selected_project = st.selectbox("בחרי פרויקט", project_names)
user_question = st.text_area("שאלה חופשית על הפרויקטים")

run = st.button("שלח ל-AI")

# =========================
# Gemini
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
    <div class="card">
        {result}
    </div>
    """, unsafe_allow_html=True)
