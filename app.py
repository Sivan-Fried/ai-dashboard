import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- הגדרות בסיסיות ---
st.set_page_config(layout="wide", page_title="Dashboard")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- פונקציה גנרית לעיצוב (הלב של המערכת) ---
def create_card(title, icon=""):
    """יוצרת מכולה עם גרדיאנט, צללית ויישור לימין"""
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(white, white) padding-box,
                        linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
            border: 2px solid transparent !important;
            border-radius: 15px !important;
            padding: 20px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
            direction: rtl !important;
        }
        .list-item {
            background: #fdfdfd; padding: 10px; border-radius: 10px;
            margin-bottom: 8px; border: 1px solid #eee;
            display: flex; align-items: center; gap: 10px; direction: rtl;
        }
        .kpi-card {
            background: white; padding: 15px; border-radius: 12px;
            text-align: center; border: 1px solid #e0e6ed;
        }
        div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton {
            text-align: right !important; direction: rtl !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        return st.container()

# --- טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("קובצי אקסל חסרים"); st.stop()

if "reminders_live" not in st.session_state: 
    st.session_state.reminders_live = reminders.copy()

# --- Header ---
img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

st.markdown(f"<h2 style='text-align:center; color:#1f2a44;'>Dashboard AI</h2>", unsafe_allow_html=True)

col_h1, col_h2, col_h3 = st.columns([1, 1, 2])
with col_h2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" style="width:120px; height:120px; border-radius:50%; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1); object-fit: cover; object-position: center 15%;"></div>', unsafe_allow_html=True)
with col_h3:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- KPI Row ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:4px solid red;'>בסיכון<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:4px solid orange;'>במעקב<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:4px solid green;'>בתקין<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- Main Content ---
col_main, col_side = st.columns([2, 1.2])

with col_main:
    with create_card("פרויקטים ומרכיבים", "📁"):
        for _, row in projects.iterrows():
            dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
            st.markdown(f'<div class="list-item"><span>{dot}</span><b>{row["project_name"]}</b></div>', unsafe_allow_html=True)

    with create_card("AI Oracle", "✨"):
        ca1, ca2, ca3 = st.columns([1, 1.5, 0.5])
        with ca1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with ca2: st.text_input("שאלה", placeholder="שאל את ה-AI...", label_visibility="collapsed", key="ai_q")
        with ca3: st.button("🚀", key="ai_go")

with col_side:
    with create_card("פגישות היום", "📅"):
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        for _, r in today_m.iterrows():
            st.markdown(f'<div class="list-item">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    with create_card("תזכורות", "🔔"):
        today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
        with st.container(height=180, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f'<div class="list-item">🔔 <b>{row["reminder_text"]}</b></div>', unsafe_allow_html=True)
        
        if st.button("➕ הוסף תזכורת"): st.session_state.show_add = True
        if st.session_state.get("show_add"):
            nt = st.text_input("מה?", key="nt")
            if st.button("✅ שמור"):
                new_r = {"reminder_text": nt, "project_name": "כללי", "date": today}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_r])], ignore_index=True)
                st.session_state.show_add = False
                st.rerun()
