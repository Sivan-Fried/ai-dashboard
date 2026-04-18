import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הזרקת CSS מסיבית (דריסה של כל רכיבי ה-Container) ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan")

st.markdown("""
<style>
    /* רקע כללי ויישור לימין */
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* העיצוב של המלבנים - דריסה מוחלטת של המכולות של Streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        margin-bottom: 25px !important;
    }

    /* תיקון צבע הכותרת הראשית שיהיה גרדיאנט נקי */
    .main-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 30px;
        font-family: sans-serif;
    }

    /* עיצוב פריטי רשימה */
    .list-item {
        background: #fdfdfd; padding: 12px; border-radius: 10px;
        margin-bottom: 10px; border: 1px solid #eee;
        display: flex; align-items: center; gap: 12px;
        text-align: right; direction: rtl;
    }

    /* עיצוב KPI */
    .kpi-card {
        background: white; padding: 15px; border-radius: 12px;
        text-align: center; border: 1px solid #e0e6ed;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    /* יישור לימין לכל רכיבי המערכת */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label, h3 {
        text-align: right !important; direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. פונקציות עזר ---
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("קובצי הנתונים חסרים"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()

# --- 4. Header & Profile (פוקוס תמונה משופר) ---
st.markdown('<div class="main-header">Dashboard AI</div>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

col_p1, col_p2, col_p3 = st.columns([1, 1, 2])
with col_p2:
    if img_b64:
        st.markdown(f'''
            <div style="display:flex; justify-content:center;">
                <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.15);">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;">
                </div>
            </div>''', unsafe_allow_html=True)
with col_p3:
    st.markdown(f"<div style='margin-top:25px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. שורת KPI ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:4px solid #ff4b4b;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:4px solid #ffa500;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:4px solid #00c853;'>בתקין 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 6. הגוף המרכזי - הכל בתוך המכולות ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # מכולת פרויקטים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
            st.markdown(f'<div class="list-item"><span>{dot}</span><b>{row["project_name"]}</b></div>', unsafe_allow_html=True)

    # מכולת AI Oracle
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        ai_col1, ai_col2 = st.columns([1, 2])
        with ai_col1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with ai_col2: st.text_input("שאלה ל-AI", placeholder="שאלי משהו...", label_visibility="collapsed", key="ai_q")
        st.button("שגר שאילתה 🚀", use_container_width=True)

with col_left:
    # מכולת פגישות
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות להיום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="list-item">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    # מכולת תזכורות
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        today_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        with st.container(height=180, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f'<div class="list-item">🔔 {row["reminder_text"]}</div>', unsafe_allow_html=True)
        
        if st.button("➕ הוסף תזכורת"): st.session_state.add_task = True
        if st.session_state.get("add_task"):
            nt = st.text_input("משימה חדשה", key="nt_new")
            if st.button("✅ שמור"):
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"reminder_text": nt, "date": today}])], ignore_index=True)
                st.session_state.add_task = False
                st.rerun()
