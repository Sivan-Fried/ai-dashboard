import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS אגרסיבי במיוחד ---
st.markdown("""
<style>
    /* רקע ויישור כללי */
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }

    /* כותרת מוקטנת עם גרדיאנט - כפייה מוחלטת */
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin: 15px 0 !important;
        display: block !important;
        width: 100% !important;
    }

    /* מסגרות הגרדיאנט - שימוש בסלקטור גורף לכל אזור עם border */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 18px !important;
        padding: 22px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
    }

    /* רשומות פנימיות עם פס תכלת */
    .record-box {
        background: #ffffff !important;
        padding: 12px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 6px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        text-align: right !important;
        color: #1f2a44 !important;
    }

    /* יישור לימין של כל רכיבי המערכת */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label, h3 {
        text-align: right !important; direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("קובצי האקסל חסרים בתיקייה"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()

# --- 4. כותרת Dashboard AI בגרדיאנט ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

# --- 5. פרופיל ---
img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64:
        st.markdown(f'''
            <div style="display:flex; justify-content:center;">
                <div style="width:120px; height:120px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 8px 16px rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;">
                </div>
            </div>''', unsafe_allow_html=True)
with p3:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 6. KPI ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k_box = "background:white; padding:15px; border-radius:12px; text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.02);"
with k1: st.markdown(f"<div style='{k_box} border-top:4px solid #ff4b4b;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div style='{k_box} border-top:4px solid #ffa500;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div style='{k_box} border-top:4px solid #00c853;'>בתקין 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div style='{k_box}'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 7. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # פרויקטים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            st.markdown(f"""
                <div class="record-box">
                    <span><b>{row['project_name']}</b></span>
                    <span style="color:gray; font-size:0.85em;">{row.get('project_type', 'פרויקט')}</span>
                </div>
            """, unsafe_allow_html=True)

    # AI Oracle
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_s")
        with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
        st.button("שגר שאילתה 🚀", use_column_width=True)

with col_left:
    # פגישות
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_meetings.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_meetings.iterrows():
                st.markdown(f'<div class="record-box"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    # תזכורות
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_rems = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        for _, row in t_rems.iterrows():
            st.markdown(f'<div class="record-box"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
        
        if st.button("➕ הוסף"): st.session_state.add_mode = True
        if st.session_state.get("add_mode"):
            nt = st.text_input("משימה:", key="nt_final")
            if st.button("שמור"):
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"reminder_text": nt, "date": today}])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
