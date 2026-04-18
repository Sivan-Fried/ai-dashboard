import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות ועיצוב (חזרה למקור + שדות לבנים באזור ה-AI)
st.set_page_config(layout="wide", page_title="Dashboard")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    
    /* כרטיסיות רגילות */
    .card {
        background:white; padding:15px; border-radius:10px;
        margin-bottom:10px; border:1px solid #eee;
        direction:rtl; text-align:right;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* אזור האורקל - AI */
    .oracle-box {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 2.5rem;
        padding: 2.5rem;
        border: 1px solid rgba(146, 152, 247, 0.4);
        box-shadow: 0 10px 40px rgba(146, 152, 247, 0.15);
        direction: rtl;
        text-align: right;
        margin-top: 30px;
    }

    /* תיקון: החזרת שדות הקלט ללבן בתוך אזור ה-AI */
    .oracle-box div[data-baseweb="select"] > div, 
    .oracle-box input {
        background-color: white !important;
        border: 1px solid #ddd !important;
    }
    
    h1, h2, h3 { color:#1f2a44; text-align:right; direction:rtl; }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית (החזרתי!)
st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# 2. פרופיל, ברכה, תאריך ושעה (החזרתי הכל למקום!)
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

l, c, r = st.columns([1.2, 1, 1.2])
with l:
    st.markdown(f"""
    <div style="direction:rtl; text-align:right; margin-top:40px; color:#1f2a44;">
        <div style="font-size:22px;">{greeting}, סיון!</div>
        <div style="font-size:13px; color:gray;">{now.strftime('%d/%m/%Y %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

with c:
    if img_base64:
        st.markdown(f"""
        <div style="display:flex; justify-content:center; margin-top:10px;">
            <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
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
    if "reminders_live" not in st.session_state: st.session_state.reminders_live = reminders.copy()
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינה: {e}")
    st.stop()

# 4. KPI
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='card'><b>סה״כ פרויקטים</b><br><h2>{len(projects)}</h2></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='card' style='border-top: 3px solid red;'><b>בסיכון 🔴</b><br><h2 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h2></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='card' style='border-top: 3px solid orange;'><b>במעקב 🟡</b><br><h2 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h2></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='card' style='border-top: 3px solid green;'><b>תקין 🟢</b><br><h2 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h2></div>", unsafe_allow_html=True)

# 5. פריסת פרויקטים ולו"ז
col_left, col_right = st.columns([1.2, 1])

with col_right:
    st.markdown("### 📁 פרויקטים")
    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        st.markdown(f"<div class='card'>{row['project_name']} <span style='float:left;'>{dot}</span></div>", unsafe_allow_html=True)

with col_left:
    st.markdown("### 📅 לו״ז ועדכונים")
    m_today = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if not m_today.empty:
        for _, row in m_today.iterrows():
            st.markdown(f"<div class='card'><b>📌 {row['meeting_title']}</b><br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)
    
    st.markdown("#### 🔔 תזכורות")
    with st.container(height=200):
        for _, row in st.session_state.reminders_live.iterrows():
            st.markdown(f"<div class='card' style='font-size:13px;'>✍️ {row['reminder_text']}</div>", unsafe_allow_html=True)
    
    if st.button("➕ הוספת תזכורת"): st.session_state.add_mode = True
    if st.session_state.get("add_mode"):
        with st.form("r_form"):
            t = st.text_input("תזכורת חדשה:")
            if st.form_submit_button("שמור"):
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([{"reminder_text": t, "date": today}])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()

# 6. אזור ה-AI המעוצב (עם שדות לבנים כפי שביקשת)
st.markdown("---")
st.markdown("<div class='oracle-box'>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-top:0; color:#5056af;'>✨ האורקל הדיגיטלי</h3>", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
ca1, ca2 = st.columns([1, 2])
with ca1:
    s_p = st.selectbox("בחר פרויקט לניתוח", projects["project_name"].tolist(), key="final_p")
with ca2:
    u_q = st.text_input("שאלי אותי כל דבר על הפרויקטים שלך...", key="final_q")

if st.button("בצע ניתוח AI"):
    if u_q:
        with st.spinner("האורקל מנתח..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {s_p}. Question: {u_q}"}]}]}, timeout=10)
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div style='background:rgba(80,86,175,0.05); padding:15px; border-radius:15px; border:1px solid #d0d3ff; margin-top:10px;'>{ans}</div>", unsafe_allow_html=True)
            except: st.error("שגיאה")

st.markdown("</div>", unsafe_allow_html=True)
