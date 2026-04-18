import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב (Vibe: Oracle Glass)
st.set_page_config(layout="wide", page_title="AI Project Dashboard")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
<style>
    body, .stApp { background-color: #f7f9fc; font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* כרטיסיית זכוכית מרכזית */
    .oracle-section {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 2.5rem;
        padding: 2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.04);
        direction: rtl;
        text-align: right;
        margin-bottom: 20px;
    }
    
    /* אפקט זוהר לאזור ה-AI */
    .ai-container {
        border: 1px solid rgba(146, 152, 247, 0.4);
        box-shadow: 0 0 20px rgba(146, 152, 247, 0.2);
        background: rgba(255, 255, 255, 0.8);
    }

    /* כרטיסיית KPI */
    .stat-card {
        padding: 1.5rem;
        border-radius: 2rem;
        border: 1px solid rgba(0,0,0,0.05);
        direction: rtl;
        text-align: right;
    }

    h3 { color: #1e1b4b; font-weight: 800; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# 2. טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    if "reminders_live" not in st.session_state: st.session_state.reminders_live = reminders.copy()
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינה: {e}")
    st.stop()

# 3. פרופיל (שמירה על פוקוס ומסגרת)
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

l, c, r = st.columns([1.2, 1, 1.2])
with l:
    st.markdown(f"<div style='direction:rtl; text-align:right; margin-top:40px;'><h2>{greeting}, סיון</h2><p style='color:#6366f1; font-weight:600;'>{now.strftime('%d/%m/%Y')}</p></div>", unsafe_allow_html=True)
with c:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center; margin-top:10px;"><div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center top;"></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. KPI - אזורים תחומים (Stat Cards)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='stat-card' style='background:#f0f4f8;'><b>סה״כ פרויקטים</b><br><span style='font-size:32px; font-weight:900;'>{len(projects)}</span></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='stat-card' style='background:#feefda;'><b>בסיכון 🔴</b><br><span style='font-size:32px; font-weight:900; color:#a8364b;'>{len(projects[projects['status']=='אדום'])}</span></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='stat-card' style='background:#e9eef3;'><b>במעקב 🟡</b><br><span style='font-size:32px; font-weight:900; color:#f59e0b;'>{len(projects[projects['status']=='צהוב'])}</span></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='stat-card' style='background:#a5f0ef;'><b>תקין 🟢</b><br><span style='font-size:32px; font-weight:900; color:#146a6a;'>{len(projects[projects['status']=='ירוק'])}</span></div>", unsafe_allow_html=True)

# 5. הגוף המרכזי (פרויקטים ותזכורות/לו"ז)
col_left, col_right = st.columns([1.3, 1])

with col_right:
    st.markdown("<div class='oracle-section'>", unsafe_allow_html=True)
    st.markdown("### 📁 פרויקטים")
    for _, row in projects.iterrows():
        color = "#22c55e" if row["status"]=="ירוק" else "#f59e0b" if row["status"]=="צהוב" else "#ef4444"
        st.markdown(f"<div style='background:white; padding:12px; border-radius:1rem; margin-bottom:8px; border-right:5px solid {color}; box-shadow:0 2px 4px rgba(0,0,0,0.02);'><b>{row['project_name']}</b><br><small style='color:gray;'>{row['project_type']}</small></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_left:
    # אזור לו"ז ופגישות (החזרתי!)
    st.markdown("<div class='oracle-section'>", unsafe_allow_html=True)
    st.markdown("### 📅 לו״ז ועדכונים")
    m_today = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if not m_today.empty:
        for _, row in m_today.iterrows():
            st.markdown(f"<div style='border-bottom:1px solid #eee; padding:10px 0;'><b>📌 {row['meeting_title']}</b><br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)
    else: st.info("אין פגישות להיום")
    
    st.markdown("<br><h4>🔔 תזכורות</h4>", unsafe_allow_html=True)
    with st.container(height=180):
        for _, row in st.session_state.reminders_live.iterrows():
            st.markdown(f"<div style='background:#f8f9fc; padding:10px; border-radius:10px; margin-bottom:5px; font-size:13px;'>✍️ {row['reminder_text']}</div>", unsafe_allow_html=True)
    
    if st.button("➕ הוספת תזכורת"): st.session_state.add_mode = True
    if st.session_state.get("add_mode"):
        with st.form("rem_form"):
            t = st.text_input("מה תרצי להוסיף?")
            if st.form_submit_button("שמור"):
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([{"reminder_text": t, "date": today}])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 6. אזור ה-AI (האורקל הדיגיטלי - בתוך הכרטיסייה היפה)
st.markdown("---")
st.markdown("<div class='oracle-section ai-container'>", unsafe_allow_html=True)
st.markdown("""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:15px;'>
        <div style='background:#5056af; padding:8px; border-radius:12px; color:white;'>✨</div>
        <h3 style='margin:0;'>האורקל הדיגיטלי</h3>
    </div>
""", unsafe_allow_html=True)

# שילוב האלמנטים של ה-AI בתוך הכרטיסייה
ca1, ca2 = st.columns([1, 2])
with ca1: 
    s_proj = st.selectbox("בחרי פרויקט לניתוח", projects["project_name"].tolist())
with ca2: 
    u_q = st.text_input("שאלי אותי כל דבר על הפרויקטים שלך...", placeholder="למשל: מה מצב פרויקט ה-UI?")

if st.button("שאל את האורקל"):
    if u_q:
        with st.spinner("מנתח..."):
            api_key = st.secrets.get("GEMINI_API_KEY")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
            res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {s_proj}. Question: {u_q}"}]}]})
            if res.status_code == 200:
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div style='background:#f0f1ff; padding:20px; border-radius:1.5rem; border:1px solid #d0d3ff; margin-top:15px; color:#1e1b4b;'>{ans}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
