import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב (חזרה למבנה היציב)
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* מעטפת אזור חיצונית */
    .section-wrap {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        direction: rtl;
        text-align: right;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* המלבן הלבן הפנימי שביקשת */
    .inner-white-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #eee;
        margin-top: 10px;
    }

    .card {
        background: white; 
        padding: 15px; 
        border-radius: 10px;
        margin-bottom: 10px; 
        border: 1px solid #eee;
        direction: rtl; 
        text-align: right;
    }

    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    .kpi-card h4 { margin: 0; font-size: 1.2rem; }
    .kpi-card p { margin: 0; font-size: 0.9rem; color: #666; }

    h3 { color: #1f2a44; text-align: right; direction: rtl; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("""
<div style="text-align:center; margin-bottom:20px;">
    <h2 style="font-weight:800; direction:rtl; font-size: 1.8rem;">
        <span class="text-gradient">Dashboard AI</span>
        <span style="color: #1f2a44;">לניהול פרויקטים</span>
    </h2>
</div>
""", unsafe_allow_html=True)

# 2. פונקציית תמונה ופרופיל (תיקון פוקוס)
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב" if 18 <= now.hour < 22 else "לילה טוב"

left, center, right = st.columns([1.2, 1, 1.2])
with left:
    st.markdown(f'<div style="direction:rtl; text-align:right; margin-top:40px;"><div style="font-size:22px;">{greeting}, סיון!</div><div style="font-size:13px; color:gray;">{now.strftime("%d/%m/%Y %H:%M")}</div></div>', unsafe_allow_html=True)
with center:
    if img_base64:
        # הוספת object-position: center 20% לתיקון הפוקוס על הפנים
        st.markdown(f'''
            <div style="display:flex; justify-content:center; margin-top:10px;">
                <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;">
                </div>
            </div>
        ''', unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("שגיאה בטעינת קבצים")
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

# 5. פרויקטים (עם התיחום המבוקש)
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
st.markdown("<h3>📁 פרויקטים</h3>", unsafe_allow_html=True)
st.markdown("<div class='inner-white-container'>", unsafe_allow_html=True)
for _, row in projects.iterrows():
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    st.markdown(f'<div style="background:white; padding:8px 10px; border-radius:8px; margin-bottom:4px; border:1px solid #eee; direction:rtl; text-align:right; font-size:14px;">{row["project_name"]} <span style="float:left;">{dot}</span></div>', unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# 6. לו"ז ותזכורות (חזרה לפונקציונליות המלאה)
col_right, col_left = st.columns(2)

with col_right:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 📅 פגישות היום")
    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_meetings.empty:
        st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"<div class='card'>📌 {row['meeting_title']}<br>🕒 {row['time']}<br>📁 {row['project_name']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_left:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 🔔 תזכורות")
    
    # הצגת תזכורות קיימות
    today_reminders = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    rem_container = st.container(height=250)
    with rem_container:
        if today_reminders.empty:
            st.info("אין תזכורות להיום 🎉")
        else:
            for _, row in today_reminders.iterrows():
                icon = "🤖" if row.get("source") == "ai" else "✍️"
                st.markdown(f"<div class='card'>{icon} {row['reminder_text']}</div>", unsafe_allow_html=True)

    # לוגיקת הוספת תזכורת המקורית
    if not st.session_state.get("add_mode"):
        if st.button("➕ הוספת תזכורת"):
            st.session_state.add_mode = True
            st.rerun()
    else:
        with st.form("new_reminder_form"):
            new_text = st.text_input("מה תרצי שאזכיר לך?")
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("שמור תזכורת ✔")
            with col2:
                if st.form_submit_button("ביטול ✖"):
                    st.session_state.add_mode = False
                    st.rerun()
            
            if submitted and new_text:
                new_row = {"reminder_text": new_text, "date": today, "source": "manual"}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 7. AI האורקל
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'>", unsafe_allow_html=True)
st.markdown("### ✨ סוכן ה-AI שלך")
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist())
with ca2: q_in = st.text_input("מה תרצי לדעת?")
if st.button("בצע ניתוח"):
    if q_in:
        with st.spinner("מנתח..."):
            api_key = st.secrets.get("GEMINI_API_KEY")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {sel_p}. Question: {q_in}"}]}]}, timeout=10)
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div class='card'>{ans}</div>", unsafe_allow_html=True)
            except: st.error("שגיאה בתקשורת")
st.markdown("</div>", unsafe_allow_html=True)
