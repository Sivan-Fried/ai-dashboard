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

# --- 2. הזרקת CSS "אלים" (Dashing Style) ---
# אנחנו משתמשים ב-Attribute Selector כדי לתפוס את המכולות גם אם ה-Class משתנה
st.markdown("""
<style>
    /* רקע כללי */
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* כותרת גרדיאנט מקובעת */
    .dashboard-title {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 20px 0;
        font-family: sans-serif;
    }

    /* עיצוב המלבנים - תפיסה ישירה של המכולה עם הגבול */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
    }

    /* פריטי רשימה מעוצבים */
    .list-item {
        background: #fdfdfd; padding: 12px; border-radius: 10px;
        margin-bottom: 10px; border: 1px solid #eee;
        display: flex; align-items: center; gap: 12px;
        text-align: right; direction: rtl;
    }

    /* KPI Cards */
    .kpi-box {
        background: white; padding: 20px; border-radius: 15px;
        text-align: center; border: 1px solid #eef2f6;
    }

    /* יישור לימין לכל האלמנטים של Streamlit */
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
    st.error("וודאי שקובצי האקסל קיימים בתיקייה"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()

# --- 4. כותרת ופרופיל ---
st.markdown('<div class="dashboard-title">Dashboard AI</div>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

cp1, cp2, cp3 = st.columns([1, 1, 2])
with col_p2 if 'col_p2' in locals() else cp2: # וידוא משתנה
    if img_b64:
        st.markdown(f'''
            <div style="display:flex; justify-content:center;">
                <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;">
                </div>
            </div>''', unsafe_allow_html=True)
with cp3:
    st.markdown(f"<div style='margin-top:25px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI Row ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-box' style='border-top:5px solid #ff4b4b;'>בסיכון 🔴<br><span style='font-size:20px; font-weight:bold;'>{len(projects[projects['status']=='אדום'])}</span></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-box' style='border-top:5px solid #ffa500;'>במעקב 🟡<br><span style='font-size:20px; font-weight:bold;'>{len(projects[projects['status']=='צהוב'])}</span></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-box' style='border-top:5px solid #00c853;'>בתקין 🟢<br><span style='font-size:20px; font-weight:bold;'>{len(projects[projects['status']=='ירוק'])}</span></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-box'>סה\"כ פרויקטים<br><span style='font-size:20px; font-weight:bold;'>{len(projects)}</span></div>", unsafe_allow_html=True)

# --- 6. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
col_r, col_l = st.columns([2, 1.2])

with col_r:
    # מלבן פרויקטים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            st.markdown(f'<div class="list-item">🔹 <b>{row["project_name"]}</b> <small style="margin-right:auto; color:gray;">{row["project_type"]}</small></div>', unsafe_allow_html=True)

    # מלבן AI Oracle
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a_col1, a_col2 = st.columns([1, 2])
        with a_col1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with a_col2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_q")
        st.button("שגר שאילתה 🚀", use_container_width=True)

with col_l:
    # פגישות
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="list-item">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    # תזכורות
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        today_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        with st.container(height=180, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f'<div class="list-item">🔔 {row["reminder_text"]}</div>', unsafe_allow_html=True)
        
        if st.button("➕ הוסף תזכורת"): st.session_state.add_mode = True
        if st.session_state.get("add_mode"):
            nt = st.text_input("משימה:", key="nt_input")
            if st.button("✅ שמור"):
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"reminder_text": nt, "date": today}])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
