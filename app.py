import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- הזרקת CSS מוחלטת ---
st.markdown("""
<style>
    /* רקע ויישור כללי */
    .stApp { background-color: #f8f9fb !important; direction: rtl !important; }
    
    /* כותרת גרדיאנט גדולה ויציבה */
    .main-title {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        margin: 20px 0 !important;
    }

    /* עיצוב המסגרות - דריסה של כל מכולה עם border=True */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    }

    /* פריטי רשימה */
    .item-box {
        background: #ffffff; padding: 12px; border-radius: 12px;
        margin-bottom: 10px; border: 1px solid #edf2f7;
        display: flex; align-items: center; gap: 12px;
    }

    /* יישור RTL לכל האלמנטים */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label {
        text-align: right !important; direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# --- טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("חסרים קבצי אקסל במערכת"); st.stop()

if "rem_data" not in st.session_state: st.session_state.rem_data = reminders.copy()

# --- Header & Profile ---
st.markdown('<h1 class="main-title">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

c1, c2, c3 = st.columns([1, 1, 2])
with c2:
    if img_b64:
        st.markdown(f'''
            <div style="display:flex; justify-content:center;">
                <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 8px 16px rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;">
                </div>
            </div>''', unsafe_allow_html=True)
with c3:
    st.markdown(f"<div style='margin-top:25px;'><h3>{greeting}, סיון!</h3><p style='color:#64748b;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- KPI Section ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k_style = "background:white; padding:20px; border-radius:15px; text-align:center; border:1px solid #e2e8f0;"
with k1: st.markdown(f"<div style='{k_style} border-top:5px solid #ef4444;'>בסיכון<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div style='{k_style} border-top:5px solid #f59e0b;'>במעקב<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div style='{k_style} border-top:5px solid #10b981;'>בתקין<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div style='{k_style}'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
main_col, side_col = st.columns([2, 1.2])

with main_col:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            st.markdown(f'<div class="item-box">🔹 <b>{row["project_name"]}</b></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with a2: st.text_input("שאל את ה-AI", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_q")
        st.button("שגר שאילתה 🚀", use_container_width=True)

with side_col:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="item-box">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        today_r = st.session_state.rem_data[pd.to_datetime(st.session_state.rem_data["date"]).dt.date == today]
        with st.container(height=180, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f'<div class="item-box">🔔 {row["reminder_text"]}</div>', unsafe_allow_html=True)
        
        if st.button("➕ הוסף תזכורת"): st.session_state.add_mode = True
        if st.session_state.get("add_mode"):
            nt = st.text_input("משימה חדשה", key="new_task")
            if st.button("✅ שמור"):
                st.session_state.rem_data = pd.concat([st.session_state.rem_data, pd.DataFrame([{"reminder_text": nt, "date": today}])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
