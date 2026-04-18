import streamlit as st
import pandas as pd
import requests
import json
import base64
import os
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS מקורי
st.set_page_config(layout="wide", page_title="AI Dashboard Stable")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    .card {
        background:white; padding:15px; border-radius:10px;
        margin-bottom:10px; border:1px solid #eee;
        direction:rtl; text-align:right;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color:#1f2a44; text-align:right; direction:rtl; }
    
    /* עיצוב שדות הקלט של ה-AI ללבן */
    div[data-baseweb="select"] > div, .stTextArea textarea {
        background-color: white !important;
        direction: rtl !important;
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# 2. פרופיל וברכה (זמן ישראל)
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
hour = now.hour

if 5 <= hour < 12: greeting = "בוקר טוב"
elif 12 <= hour < 18: greeting = "צהריים טובים"
elif 18 <= hour < 22: greeting = "ערב טוב"
else: greeting = "לילה טוב"

left, center, right = st.columns([1.2, 1, 1.2])
with left:
    st.markdown(f"""
    <div style="direction:rtl; text-align:right; margin-top:40px; color:#1f2a44;">
        <div style="font-size:22px;">{greeting}, סיון!</div>
        <div style="font-size:13px; color:gray;">{now.strftime('%d/%m/%Y %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

with center:
    if img_base64:
        st.markdown(f"""
        <div style="display:flex; justify-content:center; margin-top:10px;">
            <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:3px solid #ddd; box-shadow:0px 2px 10px rgba(0,0,0,0.15);">
                <img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover; object-position: center top;">
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 3. טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינת קבצים: {e}")
    st.stop()

# 4. KPI - חלוקה ל-4 עמודות נפרדות
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='card'><b>סה״כ פרויקטים</b><br>{len(projects)}</div>", unsafe_allow_html=True)
with c2:
    red_count = len(projects[projects['status'] == 'אדום'])
    st.markdown(f"<div class='card' style='border-top: 3px solid red;'><b>בסיכון 🔴</b><br>{red_count}</div>", unsafe_allow_html=True)
with c3:
    yellow_count = len(projects[projects['status'] == 'צהוב'])
    st.markdown(f"<div class='card' style='border-top: 3px solid orange;'><b>במעקב 🟡</b><br>{yellow_count}</div>", unsafe_allow_html=True)
with c4:
    green_count = len(projects[projects['status'] == 'ירוק'])
    st.markdown(f"<div class='card' style='border-top: 3px solid green;'><b>לפי התכנון 🟢</b><br>{green_count}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פריסה: פרויקטים בימין (col_right), לו"ז בשמאל (col_left)
col_left, col_right = st.columns([1.2, 1])

with col_right:
    st.markdown("### 📁 פרויקטים")
    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        st.markdown(f"""
        <div class="card" style="padding:10px; margin-bottom:5px; font-size:14px;">
            {row['project_name']} <span style='color:gray; font-size:11px;'>| {row['project_type']}</span>
            <span style='float:left;'>{dot}</span>
        </div>
        """, unsafe_allow_html=True)

with col_left:
    st.markdown("### 📅 לו״ז ועדכונים היום")
    
    # פגישות
    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_meetings.empty:
        st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"""
            <div class='card'>
                <b>📌 {row['meeting_title']}</b><br>
                <span style='font-size:12px; color:gray;'>🕒 {row['time']} | 📁 {row['project_name']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # תזכורות
    st.markdown("#### 🔔 תזכורות")
    reminder_container = st.container(height=250)
    with reminder_container:
        for _, row in reminders.iterrows():
            st.markdown(f"<div class='card' style='font-size:13px;'>✍️ {row['reminder_text']}</div>", unsafe_allow_html=True)

# 6. אזור ה-AI
st.markdown("---")
st.markdown("### 🤖 עוזר AI אישי")

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    ca1, ca2 = st.columns(2)
    with ca1:
        s_proj = st.selectbox("בחרי פרויקט לניתוח", projects["project_name"].tolist(), key="ai_sel_final")
    with ca2:
        u_q = st.text_area("מה תרצי לדעת?", placeholder="למשל: מהם צעדי המניעה לפרויקט באדום?", key="ai_txt_final")

    if st.button("בצע ניתוח AI"):
        if u_q:
            p_info = projects[projects["project_name"] == s_proj].iloc[0]
            context = f"פרויקט: {p_info.to_string()}. ענה בעברית תמציתית בנקודות."
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": f"{context} שאלה: {u_q}"}]}]}, timeout=10)
                if res.status_code == 200:
                    ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(f"""
                    <div style="direction: rtl; text-align: right; background-color: #d4edda; color: #155724; padding: 15px; border-radius: 10px; border: 1px solid #c3e6cb; line-height: 1.6;">
                        {ans}
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("שגיאה בתקשורת עם ה-AI")
            except: st.error("שגיאת חיבור")
