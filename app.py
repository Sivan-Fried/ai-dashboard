import streamlit as st
import pandas as pd
import base64
import os
import datetime
import google.generativeai as genai

st.set_page_config(layout="wide")

# =========================
# עיצוב
# =========================
st.markdown("""
<style>
body {
    background-color: #f2f4f7;
}

.stApp {
    background-color: #f2f4f7;
}

.card {
    background:white;
    padding:8px 10px;
    border-radius:8px;
    margin-bottom:6px;
    border:1px solid #eee;
    direction:rtl;
    text-align:right;
    font-size:14px;
}

h1, h2, h3 {
    color:#1f2a44;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# =========================
# פרופיל
# =========================
def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("profile.png")

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))

hour = now.hour

if 5 <= hour < 12:
    greeting = "בוקר טוב"
elif 12 <= hour < 18:
    greeting = "צהריים טובים"
elif 18 <= hour < 22:
    greeting = "ערב טוב"
else:
    greeting = "לילה טוב"

date_str = now.strftime("%d/%m/%Y %H:%M")

left, center, right = st.columns([1.2, 1, 1.2])

with left:
    st.markdown(f"""
    <div style="direction:rtl;text-align:right;margin-top:40px;color:#1f2a44;">
        <div style="font-size:22px;">{greeting}, סיון!</div>
        <div style="font-size:13px;color:gray;">{date_str}</div>
    </div>
    """, unsafe_allow_html=True)

with center:
    st.markdown(f"""
    <div style="display:flex;justify-content:center;margin-top:10px;">
        <div style="width:140px;height:140px;border-radius:50%;overflow:hidden;border:3px solid #ddd;">
            <img src="data:image/png;base64,{img_base64}"
            style="width:100%;height:100%;object-fit:cover;">
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.write("")

st.markdown("---")

# =========================
# נתונים
# =========================
projects = pd.read_excel("my_projects.xlsx")
meetings = pd.read_excel("meetings.xlsx")
reminders = pd.read_excel("reminders.xlsx")

today = pd.Timestamp.today().date()

# =========================
# AI תזכורות
# =========================
def generate_ai_reminders(df):
    ai = []
    for _, row in df.iterrows():
        if row["status"] in ["צהוב", "אדום"]:
            ai.append({
                "reminder_text": f"התחלה/מעקב על {row['project_name']}",
                "project_name": row["project_name"],
                "date": today,
                "priority": "medium",
                "source": "ai"
            })
    return pd.DataFrame(ai)

ai_reminders = generate_ai_reminders(projects)

if "reminders_live" not in st.session_state:
    st.session_state.reminders_live = pd.concat([reminders, ai_reminders], ignore_index=True)

# =========================
# KPI
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"<div class='card'><b>סה״כ פרויקטים</b><br>{len(projects)}</div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"<div class='card'><b>בסיכון 🔴</b><br>{len(projects[projects['status']=='אדום'])}</div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"<div class='card'><b>במעקב 🟡</b><br>{len(projects[projects['status']=='צהוב'])}</div>", unsafe_allow_html=True)

st.markdown("---")

# =========================
# פרויקטים
# =========================
st.markdown("### 📁 פרויקטים")

for _, row in projects.iterrows():
    st.markdown(f"""
    <div class='card'>
        {row['project_name']} | {row['project_type']} | {row['status']}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =========================
# פגישות + תזכורות
# =========================
col_right, col_left = st.columns(2)

with col_right:
    st.markdown("### 📅 פגישות היום")

    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]

    if today_meetings.empty:
        st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"""
            <div class='card'>
                📌 {row['meeting_title']}<br>
                🕒 {row['time']}<br>
                📁 {row['project_name']}
            </div>
            """, unsafe_allow_html=True)

with col_left:
    st.markdown("### 🔔 תזכורות")

    today_reminders = st.session_state.reminders_live[
        pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today
    ]

    container = st.container(height=260)

    with container:
        if today_reminders.empty:
            st.info("אין תזכורות להיום 🎉")
        else:
            for _, row in today_reminders.iterrows():
                icon = "🤖" if row["source"] == "ai" else "✍️"
                st.markdown(f"""
                <div class="card">
                    {icon} {row['reminder_text']} | 📁 {row['project_name']}
                </div>
                """, unsafe_allow_html=True)

# =========================
# 🤖 AI AREA (תיקון סופי שעובד)
# =========================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Missing GEMINI_API_KEY")
    st.stop()

genai.configure(api_key=api_key)

# 🔥 מודל יציב שעובד בלי 404
model = genai.GenerativeModel("gemini-1.0-pro")

st.markdown("---")
st.markdown("### 🤖 אזור AI")

ai_col1, ai_col2 = st.columns(2)

with ai_col1:
    selected_project = st.selectbox(
        "בחרי פרויקט",
        projects["project_name"].tolist(),
        key="ai_project"
    )

with ai_col2:
    question = st.text_area(
        "שאלה חופשית",
        key="ai_question"
    )

if st.button("שלח ל-AI"):

    if not question.strip():
        st.warning("אנא הזיני שאלה")
        st.stop()

    row = projects[projects["project_name"] == selected_project].iloc[0]

    prompt = f"""
את עוזרת לניהול פרויקטים.

פרויקט:
{row['project_name']} - {row['status']}

שאלה:
{question}

עני בעברית קצר וברור.
"""

    try:
        response = model.generate_content(prompt)
        result = response.text
    except Exception as e:
        result = f"⚠️ שגיאה: {str(e)}"

    st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)
