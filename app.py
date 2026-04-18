import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות ועיצוב UI המבוסס על ה-Vibe של "האורקל הדיגיטלי"
st.set_page_config(layout="wide", page_title="AI Dashboard - Digital Oracle Vibe")

# הטמעת הפונט והסטייל מהקוד ששלחת
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
<style>
    /* עיצוב כללי לפי הקוד שסיפקת */
    body, .stApp { 
        background-color: #f7f9fc; 
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* כרטיסיית הזכוכית המדויקת של האורקל */
    .oracle-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 2.5rem; /* עיגול פינות עמוק כמו בקוד */
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.04);
        direction: rtl;
        text-align: right;
        margin-bottom: 20px;
    }
    
    /* אפקט ה-Glow של ה-AI */
    .ai-glow {
        box-shadow: 0 0 20px rgba(146, 152, 247, 0.3);
        border-top: 1px solid rgba(146, 152, 247, 0.5);
    }

    /* כותרות בסגנון אינדיגו */
    h1, h2, h3 { color: #1e1b4b; font-weight: 800; direction: rtl; }
    
    /* שדות קלט מותאמים */
    div[data-baseweb="select"] > div, .stTextArea textarea {
        background-color: white !important;
        border-radius: 1rem !important;
        border: 2px solid #e0e7ff !important;
        direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. פונקציות עזר וטעינה
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    if "reminders_live" not in st.session_state: st.session_state.reminders_live = reminders.copy()
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינה: {e}")
    st.stop()

# 3. פרופיל וברכה (שמירה על מבנה ופוקוס תמונה)
img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

l, c, r = st.columns([1.2, 1, 1.2])
with l:
    st.markdown(f"<div style='direction:rtl; text-align:right; margin-top:40px;'><h2 style='margin-bottom:0;'>{greeting}, סיון</h2><p style='color:#6366f1; font-weight:600;'>{now.strftime('%d/%m/%Y')}</p></div>", unsafe_allow_html=True)

with c:
    if img_b64:
        st.markdown(f"""
        <div style="display:flex; justify-content:center; margin-top:10px;">
            <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
                <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center top;">
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. KPI - סגנון כרטיסיות צבעוניות מהקוד שלך
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='oracle-card' style='background:#e0e7ff;'><b>סה״כ פרויקטים</b><br><h2 style='margin:0;'>{len(projects)}</h2></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='oracle-card' style='background:#fee2e2; border-right: 5px solid #ef4444;'><b>בסיכון 🔴</b><br><h2 style='margin:0; color:#ef4444;'>{len(projects[projects['status']=='אדום'])}</h2></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='oracle-card' style='background:#fef3c7; border-right: 5px solid #f59e0b;'><b>במעקב 🟡</b><br><h2 style='margin:0; color:#f59e0b;'>{len(projects[projects['status']=='צהוב'])}</h2></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='oracle-card' style='background:#dcfce7; border-right: 5px solid #22c55e;'><b>תקין 🟢</b><br><h2 style='margin:0; color:#22c55e;'>{len(projects[projects['status']=='ירוק'])}</h2></div>", unsafe_allow_html=True)

# 5. גוף הדשבורד (פרויקטים בימין)
col_left, col_right = st.columns([1.3, 1])

with col_right:
    st.markdown("### 📁 פרויקטים")
    for _, row in projects.iterrows():
        color = "#22c55e" if row["status"]=="ירוק" else "#f59e0b" if row["status"]=="צהוב" else "#ef4444"
        st.markdown(f"""
        <div class="oracle-card" style="padding:15px; margin-bottom:10px; border-right: 6px solid {color}; border-radius:1.5rem;">
            <div style="font-weight:bold; font-size:16px;">{row['project_name']}</div>
            <div style="font-size:12px; color:#64748b;">{row['project_type']}</div>
        </div>
        """, unsafe_allow_html=True)

with col_left:
    st.markdown("### 📅 לו״ז ועדכונים")
    m_today = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if not m_today.empty:
        for _, row in m_today.iterrows():
            st.markdown(f"<div class='oracle-card'><b>📌 {row['meeting_title']}</b><br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)
    
    st.markdown("#### 🔔 תזכורות")
    with st.container(height=250):
        for _, row in st.session_state.reminders_live.iterrows():
            st.markdown(f"<div class='oracle-card' style='padding:12px; font-size:14px; border-radius:1rem;'>✍️ {row['reminder_text']}</div>", unsafe_allow_html=True)
    
    if st.button("➕ הוספת תזכורת"): st.session_state.add_mode = True
    if st.session_state.get("add_mode"):
        with st.form("new_r"):
            t = st.text_input("מה להזכיר?")
            if st.form_submit_button("שמור"):
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([{"reminder_text": t, "date": today}])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()

# 6. אזור ה-AI (האורקל הדיגיטלי)
st.markdown("---")
st.markdown("<h3 style='color:#4f46e5;'>✨ האורקל הדיגיטלי</h3>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='oracle-card ai-glow'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1: s_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist())
    with c2: q = st.text_input("שאלי אותי כל דבר על הפרויקטים שלך...", key="ai_q")
    
    if st.button("שאל את האורקל"):
        if q:
            with st.spinner("מנתח נתונים..."):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={st.secrets.get('GEMINI_API_KEY')}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {s_p}. Question: {q}"}]}]})
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div style='background:rgba(79, 70, 229, 0.05); padding:15px; border-radius:1rem; border:1px solid #e0e7ff; margin-top:10px;'>{ans}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
