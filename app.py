import streamlit as st
import pandas as pd
import base64
import os
import datetime
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

# =========================
# כותרת
# =========================
st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# =========================
# פרופיל + ברכה (יציב, בלי לשבור תמונה)
# =========================
import datetime

# ---- ברכה ----
now = datetime.datetime.now()
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

# ---- פריסה ----
col1, col2 = st.columns([1,1])

# ---- טקסט (משמאל) ----
with col1:
    st.markdown(
        f"""
        <div style="direction:rtl; text-align:right; margin-top:40px;">
            <div style="font-size:22px; color:#1f2a44;">
                {greeting}, סיון!
            </div>
            <div style="font-size:14px; color:gray;">
                {date_str}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---- תמונה (בדיוק כמו שהיה!) ----
with col2:

    def get_base64_image(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    img_base64 = get_base64_image("profile.png")

    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 10px;
    ">
        <div style="
            width:140px;
            height:140px;
            border-radius:50%;
            overflow:hidden;
            border:3px solid #ddd;
            box-shadow:0px 2px 10px rgba(0,0,0,0.15);
        ">
            <img src="data:image/png;base64,{img_base64}" style="
                width:100%;
                height:100%;
                object-fit: cover;
                object-position: center top;
            ">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# פרויקטים
# =========================
st.markdown("### 📁 פרויקטים")
st.dataframe(projects, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =========================
# 🔥 חשוב – הגדרת עמודות (לא לגעת!)
# =========================
col_right, col_left = st.columns(2)

# -------- פגישות --------
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

# -------- תזכורות --------
with col_left:

    st.markdown("### 🔔 תזכורות")

    today_reminders = st.session_state.reminders_live[
        pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today
    ]

    # 🔥 גלילה אמיתית
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
    # ➕ הוספה
    # =========================
    st.markdown("---")

    if "add_mode" not in st.session_state:
        st.session_state.add_mode = False

    if not st.session_state.add_mode:

        if st.button("➕ הוספת תזכורת"):
            st.session_state.add_mode = True
            st.rerun()

    else:

        col1, col2, col3, col4 = st.columns([5, 3, 2, 1])

        with col1:
            text = st.text_input("", placeholder="תזכורת חדשה")

        with col2:
            project = st.selectbox("", projects["project_name"].tolist())

        with col3:
            priority = st.selectbox("", ["נמוכה", "בינונית", "גבוהה"])

        with col4:
            if st.button("✔"):

                reverse = {"נמוכה":"low","בינונית":"medium","גבוהה":"high"}

                new_row = {
                    "reminder_text": text,
                    "project_name": project,
                    "date": today,
                    "priority": reverse[priority],
                    "source": "manual"
                }

                st.session_state.reminders_live.loc[len(st.session_state.reminders_live)] = new_row

                st.session_state.add_mode = False
                st.rerun()

# =========================
# AI
# =========================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### 🤖 אזור AI")

selected = st.selectbox("בחרי פרויקט", projects["project_name"].tolist())
question = st.text_area("שאלה חופשית")

if st.button("שלח ל-AI"):

    row = projects[projects["project_name"] == selected].iloc[0]

    prompt = f"""
את עוזרת לניהול פרויקטים.

פרויקטים:
{projects.to_string(index=False)}

פרויקט:
{row['project_name']} - {row['status']}

שאלה:
{question}

ענה בעברית קצר וברור
"""

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        result = model.generate_content(prompt).text
    except Exception as e:
        result = str(e)

    st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)
    
