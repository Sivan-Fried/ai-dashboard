import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    .card {
        background: white; 
        padding: 15px; 
        border-radius: 10px;
        margin-bottom: 10px; 
        border: 1px solid #eee;
        direction: rtl; 
        text-align: right;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #1f2a44; text-align: right; direction: rtl; }
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] input {
        background-color: white !important;
        direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# 2. פרופיל
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
today = pd.Timestamp.today().date()

left, center, right = st.columns([1.2, 1, 1.2])
with left:
    st.markdown(f"<div style='direction:rtl; text-align:right; margin-top:40px;'><div>{now.strftime('%d/%m/%Y %H:%M')}</div></div>", unsafe_allow_html=True)
with center:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center; margin-top:10px;"><div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover; object-position: center top;"></div></div>', unsafe_allow_html=True)

# 3. נתונים
projects = pd.read_excel("my_projects.xlsx")
meetings = pd.read_excel("meetings.xlsx")
reminders = pd.read_excel("reminders.xlsx")

# לוגיקת AI לתזכורות
def generate_ai_reminders(df):
    ai = []
    for _, row in df.iterrows():
        if row["status"] in ["צהוב", "אדום"]:
            ai.append({
                "reminder_text": f"מעקב דחוף: {row['project_name']}",
                "project_name": row["project_name"],
                "date": today,
                "source": "ai"
            })
    return pd.DataFrame(ai)

if "reminders_live" not in st.session_state:
    ai_df = generate_ai_reminders(projects)
    st.session_state.reminders_live = pd.concat([reminders, ai_df], ignore_index=True)

# 4. KPI
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='card'><b>סה״כ פרויקטים</b><br>{len(projects)}</div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='card'><b>בסיכון 🔴</b><br>{len(projects[projects['status']=='אדום'])}</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='card'><b>במעקב 🟡</b><br>{len(projects[projects['status']=='צהוב'])}</div>", unsafe_allow_html=True)

# 5. פרויקטים
st.markdown("### 📁 פרויקטים")
for _, row in projects.iterrows():
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    st.markdown(f"<div class='card'>{row['project_name']} <span style='color:gray; font-size:12px;'>| {row['project_type']}</span> <span style='float:left;'>{dot}</span></div>", unsafe_allow_html=True)

st.markdown("---")

# 6. הגדרת עמודות ללו"ז ותזכורות
col_meetings, col_reminders = st.columns(2)

with col_meetings:
    st.markdown("### 📅 פגישות היום")
    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_meetings.empty:
        st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"<div class='card'>📌 {row['meeting_title']}<br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)

with col_reminders:
    st.markdown("### 🔔 תזכורות")
    
    # --- התיקון כאן: מציג הכל, או מסנן רק לכאלו שהתאריך שלהן עבר/הגיע ---
    display_reminders = st.session_state.reminders_live.copy()
    # אם רוצים לסנן רק להיום ומטה (כולל כאלו שאין להם תאריך):
    display_reminders["date_dt"] = pd.to_datetime(display_reminders["date"]).dt.date
    relevant_reminders = display_reminders[(display_reminders["date_dt"] <= today) | (display_reminders["date_dt"].isna())]

    container = st.container(height=300)
    with container:
        if relevant_reminders.empty:
            st.info("אין תזכורות 🎉")
        else:
            for _, row in relevant_reminders.iterrows():
                icon = "🤖" if row.get("source") == "ai" else "✍️"
                p_name = row.get("project_name", "כללי")
                st.markdown(f"""
                <div class="card">
                    {icon} {row['reminder_text']} | <small style='color:blue;'>{p_name}</small>
                </div>
                """, unsafe_allow_html=True)

    # כפתור הוספה
    if st.button("➕ הוספת תזכורת"):
        st.session_state.add_mode = True
    
    if st.session_state.get("add_mode"):
        with st.form("new_rem"):
            t = st.text_input("מה התזכורת?")
            p = st.selectbox("פרויקט", projects["project_name"].tolist())
            if st.form_submit_button("שמור"):
                new_row = {"reminder_text": t, "project_name": p, "date": today, "source": "manual"}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()

# 7. AI Oracle
st.markdown("---")
st.markdown("### ✨ האורקל הדיגיטלי")
ca1, ca2 = st.columns([1, 2])
with ca1: s_p = st.selectbox("פרויקט לניתוח", projects["project_name"].tolist())
with ca2: u_q = st.text_input("שאלי את האורקל...")

if st.button("שאל"):
    api_key = st.secrets.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
    res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {s_p}. Question: {u_q}"}]}]})
    if res.status_code == 200:
        st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
