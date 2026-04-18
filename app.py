import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות ועיצוב UI בסגנון Glassmorphism (מספר 2)
st.set_page_config(layout="wide", page_title="AI Dashboard Glass Edition")

st.markdown("""
<style>
    /* רקע עם גרדיאנט עדין כדי להבליט את אפקט הזכוכית */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
    }
    
    /* כרטיסיות זכוכית (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.7); /* שקיפות */
        backdrop-filter: blur(10px); /* אפקט טשטוש */
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        background: rgba(255, 255, 255, 0.85);
        transform: translateY(-2px);
    }
    
    /* עיצוב שורות פרויקטים מצומצמות בסגנון זכוכית */
    .project-row-glass {
        background: rgba(255, 255, 255, 0.5);
        padding: 12px 18px;
        border-radius: 12px;
        margin-bottom: 8px;
        border-right: 6px solid #ddd;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* התאמת שדות הקלט שיראו חלק מהעיצוב */
    div[data-baseweb="select"] > div, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }
    
    h1, h2, h3, h4 { color: #1f2a44; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# 2. טעינת נתונים וניהול מצב (ללא שינוי)
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    if "reminders_live" not in st.session_state:
        st.session_state.reminders_live = reminders.copy()
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה: {e}")
    st.stop()

# 3. פרופיל וברכה (שמירה על מבנה מקורי)
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

l, c, r = st.columns([1.2, 1, 1.2])
with l: st.markdown(f"<div style='direction:rtl; text-align:right; margin-top:40px;'><h3>{greeting}, סיון!</h3><p style='color:#5a67d8; font-weight:600;'>{now.strftime('%d/%m/%Y')}</p></div>", unsafe_allow_html=True)
with c:
    if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid rgba(255,255,255,0.8); box-shadow:0 10px 25px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit:cover;"></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. KPI בסגנון Glassmorphism
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='glass-card'><b>סה״כ פרויקטים</b><br><h2 style='margin:0; color:#2d3748;'>{len(projects)}</h2></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='glass-card' style='border-bottom: 4px solid #ff4b4b;'><b>בסיכון 🔴</b><br><h2 style='margin:0; color:#ff4b4b;'>{len(projects[projects['status']=='אדום'])}</h2></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='glass-card' style='border-bottom: 4px solid #ffa500;'><b>במעקב 🟡</b><br><h2 style='margin:0; color:#ffa500;'>{len(projects[projects['status']=='צהוב'])}</h2></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='glass-card' style='border-bottom: 4px solid #28a745;'><b>תקין 🟢</b><br><h2 style='margin:0; color:#28a745;'>{len(projects[projects['status']=='ירוק'])}</h2></div>", unsafe_allow_html=True)

# 5. פריסה: פרויקטים בימין, לו"ז בשמאל
col_left, col_right = st.columns([1.2, 1])

with col_right:
    st.markdown("### 📁 סטטוס פרויקטים")
    for _, row in projects.iterrows():
        color = "#28a745" if row["status"]=="ירוק" else "#ffa500" if row["status"]=="צהוב" else "#ff4b4b"
        st.markdown(f"""
        <div class="project-row-glass" style="border-right-color: {color};">
            <div><b>{row['project_name']}</b> <br> <span style="font-size:11px; color:#718096;">{row['project_type']}</span></div>
            <div style="font-size:18px;">{"🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"}</div>
        </div>
        """, unsafe_allow_html=True)

with col_left:
    st.markdown("### 📅 לו״ז ועדכונים")
    m_today = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if not m_today.empty:
        for _, row in m_today.iterrows():
            st.markdown(f"<div class='glass-card'><b>📌 {row['meeting_title']}</b><br><small>🕒 {row['time']} | 📁 {row['project_name']}</small></div>", unsafe_allow_html=True)
    
    st.markdown("#### 🔔 תזכורות")
    with st.container(height=230):
        for _, row in st.session_state.reminders_live.iterrows():
            st.markdown(f"<div class='glass-card' style='padding:12px; margin-bottom:8px; font-size:13px;'>✍️ {row['reminder_text']}</div>", unsafe_allow_html=True)
    
    if st.button("➕ הוספת תזכורת"): st.session_state.add_mode = True
    if st.session_state.get("add_mode"):
        with st.form("add_rem"):
            t = st.text_input("תזכורת:")
            p = st.selectbox("פרויקט", projects["project_name"].tolist())
            if st.form_submit_button("שמור"):
                new = {"reminder_text": t, "project_name": p, "date": today}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()

# 6. AI Zone
st.markdown("---")
st.markdown("### 🤖 עוזר AI אישי")
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    c1, c2 = st.columns(2)
    with c1: sel_p = st.selectbox("פרויקט לניתוח", projects["project_name"].tolist())
    with c2: q = st.text_area("מה תרצי לדעת?", height=70)
    
    if st.button("נתח עם AI"):
        if q:
            with st.spinner("חושב..."):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
                try:
                    res = requests.post(url, json={"contents": [{"parts": [{"text": f"פרויקט: {sel_p}. שאלה: {q}"}]}]}, timeout=10)
                    ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(f"<div class='glass-card' style='background: rgba(212, 237, 218, 0.6); border: 1px solid #c3e6cb;'>{ans}</div>", unsafe_allow_html=True)
                except: st.error("שגיאה")
