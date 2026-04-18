import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב (תיחום אזורים וכותרת מעודנת)
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    
    /* גרדיאנט עדין לכותרת ולמסגרות */
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* מעטפת אזור עם מסגרת גרדיאנט - כוללת את כל תוכן האזור */
    .section-wrap {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 25px;
        direction: rtl;
        text-align: right;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* כותרות בתוך האזורים */
    .section-wrap h3 {
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 1.3rem;
        color: #1f2a44;
    }

    /* רשומות פנימיות נקיות */
    .card {
        background: white; 
        padding: 12px; 
        border-radius: 8px;
        margin-bottom: 8px; 
        border: 1px solid #eee;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* KPI קומפקטי */
    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    .kpi-card h4 { margin: 0; font-size: 1.2rem; }
    .kpi-card p { margin: 0; font-size: 0.85rem; color: #666; }

    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] input {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית מוקטנת ואלגנטית
st.markdown("""
<div style="text-align:center; margin-bottom:20px;">
    <h2 style="font-weight:800; direction:rtl; font-size: 1.8rem;">
        <span class="text-gradient">📊 Dashboard AI</span>
        <span style="color: #1f2a44;">לניהול פרויקטים</span>
    </h2>
</div>
""", unsafe_allow_html=True)

# 2. פונקציית תמונה ופרופיל
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
hour = now.hour
greeting = "בוקר טוב" if 5 <= hour < 12 else "צהריים טובים" if 12 <= hour < 18 else "ערב טוב" if 18 <= hour < 22 else "לילה טוב"

left, center, right = st.columns([1.2, 1, 1.2])
with left:
    st.markdown(f'<div style="direction:rtl; text-align:right; margin-top:20px; color:#1f2a44;"><div style="font-size:20px;">{greeting}, סיון!</div><div style="font-size:12px; color:gray;">{now.strftime("%d/%m/%Y %H:%M")}</div></div>', unsafe_allow_html=True)
with center:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:100px; height:100px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 5px 15px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover;"></div></div>', unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינת קבצים: {e}")
    st.stop()

if "reminders_live" not in st.session_state:
    st.session_state.reminders_live = reminders.copy()

# 4. KPI 
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><p>סה״כ פרויקטים</p><h4>{len(projects)}</h4></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid red;'><p>בסיכון 🔴</p><h4 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h4></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid orange;'><p>במעקב 🟡</p><h4 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h4></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid green;'><p>לפי התכנון 🟢</p><h4 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h4></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים - עטופים בתוך ה-Wrap המעוצב
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
st.markdown("<h3>📁 פרויקטים פעילים</h3>", unsafe_allow_html=True)

for _, row in projects.iterrows():
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    st.markdown(f"""
    <div class="card">
        {row['project_name']} <span style="color:gray; font-size:11px;">| {row['project_type']}</span> <span style="float:left;">{dot}</span>
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 6. לו"ז ותזכורות - כל אזור בתיחום מלא
col_right, col_left = st.columns(2)

with col_right:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 📅 פגישות היום")
    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_meetings.empty:
        st.info("אין פגישות היום")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"<div class='card'>📌 {row['meeting_title']}<br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_left:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 🔔 תזכורות")
    today_reminders = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    
    rem_container = st.container(height=200)
    with rem_container:
        if today_reminders.empty:
            st.info("אין תזכורות להיום")
        else:
            for _, row in today_reminders.iterrows():
                icon = "🤖" if row.get("source") == "ai" else "✍️"
                st.markdown(f"<div class='card'>{icon} {row['reminder_text']}</div>", unsafe_allow_html=True)
    
    if st.button("➕ הוספה"): st.session_state.add_mode = True
    if st.session_state.get("add_mode"):
        with st.form("new_rem_form"):
            t = st.text_input("תזכורת:")
            if st.form_submit_button("✔"):
                new_row = {"reminder_text": t, "date": today, "source": "manual"}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 7. AI האורקל - תיחום מלא
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'>", unsafe_allow_html=True)
st.markdown("### ✨ האורקל הדיגיטלי")
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="oracle_p")
with ca2: q_in = st.text_input("מה תרצי לדעת?", key="oracle_q")

if st.button("שאל את האורקל"):
    if q_in:
        with st.spinner("מנתח..."):
            api_key = st.secrets.get("GEMINI_API_KEY")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {sel_p}. Question: {q_in}"}]}]}, timeout=10)
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div class='card' style='background-color:#f8f9fa;'>{ans}</div>", unsafe_allow_html=True)
            except: st.error("שגיאה בתקשורת")
st.markdown("</div>", unsafe_allow_html=True)
