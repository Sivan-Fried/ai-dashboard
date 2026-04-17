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
reminders = pd.read_excel("reminders.xlsx", engine="openpyxl")

# =========================
# תזכורות AI
# =========================
def generate_ai_reminders(projects_df):
    ai_list = []

    for _, row in projects_df.iterrows():

        if row["status"] in ["צהוב", "אדום"]:
            ai_list.append({
                "reminder_text": f"התחלה/מעקב על {row['project_name']}",
                "project_name": row["project_name"],
                "date": pd.Timestamp.today().date(),
                "priority": "high",
                "source": "ai"
            })

    return pd.DataFrame(ai_list)

ai_reminders = generate_ai_reminders(projects)
all_reminders = pd.concat([reminders, ai_reminders], ignore_index=True)

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

with col_left:
    st.markdown("### 🚨 התראות")

    for _, row in projects.iterrows():
        icon = "🔴" if row["status"] == "אדום" else "🟡" if row["status"] == "צהוב" else "🟢"
        label = "פרויקט בסיכון" if row["status"] == "אדום" else "דורש מעקב" if row["status"] == "צהוב" else "תקין"

        st.markdown(f"""
        <div class="card">
            {icon} {label}<br>
            {row['project_name']}
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 📁 פרויקטים")
    st.dataframe(projects, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =========================
# פגישות
# =========================
st.markdown("### 📅 פגישות היום")

today = pd.Timestamp.today().date()
today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]

if today_meetings.empty:
    st.info("אין פגישות היום 🎉")
else:
    for _, row in today_meetings.iterrows():
        st.markdown(f"""
        <div class="card">
            📌 {row['meeting_title']}<br>
            🕒 {row['time']}<br>
            📁 {row['project_name']}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =========================
# תזכורות
# =========================
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("### 🔔 תזכורות")

today_reminders = all_reminders[pd.to_datetime(all_reminders["date"]).dt.date == today]

if today_reminders.empty:
    st.info("אין תזכורות להיום 🎉")

else:
    st.markdown("#### 🤖 תזכורות שנוצרו ע״י סוכן ה-AI שלך")

    for _, row in today_reminders.iterrows():

        icon = "🤖" if row["source"] == "ai" else "✍️"

        st.markdown(f"""
        <div style="
            background:white;
            padding:8px 10px;
            border-radius:8px;
            margin-bottom:6px;
            direction:rtl;
            text-align:right;
            font-size:14px;
            border:1px solid #eee;
        ">
            {icon} {row['reminder_text']} 
            <span style="color:#888;">| 📁 {row['project_name']}</span>
        </div>
        """, unsafe_allow_html=True)
        
# =========================
# AI (Gemini)
# =========================
st.markdown("### 🤖 אזור AI")

project_names = projects["project_name"].tolist()

selected_project = st.selectbox("בחרי פרויקט", project_names)
user_question = st.text_area("שאלה חופשית על הפרויקטים")

run = st.button("שלח ל-AI")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ שגיאה: {e}"

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
