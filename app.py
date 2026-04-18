import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב בסיסי מקורי
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
    
    /* שמירה על שדות קלט לבנים ונקיים */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] input {
        background-color: white !important;
        direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית מקורית
st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

# 2. פונקציית תמונה ופרופיל
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
            <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
                <img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover; object-position: center top;">
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
projects = pd.read_excel("my_projects.xlsx")
meetings = pd.read_excel("meetings.xlsx")
reminders = pd.read_excel("reminders.xlsx")
today = pd.Timestamp.today().date()

# AI תזכורות
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

# 4. KPI
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='card'><b>סה״כ פרויקטים</b><br>{len(projects)}</div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='card'><b>בסיכון 🔴</b><br>{len(projects[projects['status']=='אדום'])}</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='card'><b>במעקב 🟡</b><br>{len(projects[projects['status']=='צהוב'])}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים
st.markdown("<h3 style='text-align:right; direction:rtl;'>📁 פרויקטים</h3>", unsafe_allow_html=True)

def type_icon(project_type):
    if project_type == "פרויקט אקטיבי": return "🚀"
    elif project_type == "חבילת עבודה": return "📦"
    elif project_type == "תחזוקה": return "🔧"
    else: return "📁"

def status_dot(status):
    if status == "ירוק": return "🟢"
    elif status == "צהוב": return "🟡"
    else: return "🔴"

for _, row in projects.iterrows():
    icon = type_icon(row["project_type"])
    dot = status_dot(row["status"])
    st.markdown(f"""
    <div style="background:white; padding:8px 10px; border-radius:8px; margin-bottom:4px; border:1px solid #eee; direction:rtl; text-align:right; font-size:14px;">
        {icon} {row['project_name']}
        <span style="color:gray; font-size:12px;"> | {row['project_type']}</span>
        <span style="float:left;">{dot}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 6. לו"ז ותזכורות
col_right, col_left = st.columns(2)

with col_right:
    st.markdown("### 📅 פגישות היום")
    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_meetings.empty:
        st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"<div class='card'>📌 {row['meeting_title']}<br>🕒 {row['time']}<br>📁 {row['project_name']}</div>", unsafe_allow_html=True)

with col_left:
    st.markdown("### 🔔 תזכורות")
    today_reminders = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    
    container = st.container(height=260)
    with container:
        if today_reminders.empty:
            st.info("אין תזכורות להיום 🎉")
        else:
            for _, row in today_reminders.iterrows():
                icon = "🤖" if row["source"] == "ai" else "✍️"
                st.markdown(f"<div class='card'>{icon} {row['reminder_text']} | 📁 {row['project_name']}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if "add_mode" not in st.session_state: st.session_state.add_mode = False

    if not st.session_state.add_mode:
        if st.button("➕ הוספת תזכורת"):
            st.session_state.add_mode = True
            st.rerun()
    else:
        col1, col2, col3, col4 = st.columns([5, 3, 2, 1])
        with col1: text = st.text_input("", placeholder="תזכורת חדשה")
        with col2: project = st.selectbox("", projects["project_name"].tolist())
        with col3: priority = st.selectbox("", ["נמוכה", "בינונית", "גבוהה"])
        with col4:
            if st.button("✔"):
                p_map = {"נמוכה":"low","בינונית":"medium","גבוהה":"high"}
                new_row = {"reminder_text": text, "project_name": project, "date": today, "priority": p_map[priority], "source": "manual"}
                st.session_state.reminders_live.loc[len(st.session_state.reminders_live)] = new_row
                st.session_state.add_mode = False
                st.rerun()

# 7. AI
st.markdown("---")
st.markdown("### ✨ שאל את ה-AI על הפרויקטים")
api_key = st.secrets.get("GEMINI_API_KEY")
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_sel")
with ca2: q_in = st.text_input("מה תרצי לדעת?", key="q_in")

if st.button("בצע ניתוח"):
    if q_in:
        with st.spinner("מנתח נתונים..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {sel_p}. Question: {q_in}"}]}]}, timeout=10)
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div class='card' style='background-color:#f8f9fa;'>{ans}</div>", unsafe_allow_html=True)
            except: st.error("שגיאה בתקשורת")
