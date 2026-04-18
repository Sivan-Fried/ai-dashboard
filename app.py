import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS "הגרזן" - דריסה מוחלטת של הגדרות המערכת למסגרות וגרדיאנטים ---
st.markdown("""
<style>
    /* רקע כללי */
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* כותרת Dashboard AI מוקטנת עם גרדיאנט */
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
        display: block !important;
    }

    /* תיקון פוקוס תמונה עגולה */
    .profile-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .profile-img {
        width: 130px;
        height: 130px;
        border-radius: 50% !important;
        object-fit: cover !important;
        object-position: center 20% !important;
        border: 4px solid white !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    /* כפיית מסגרות הגרדיאנט על כל קונטיינר עם Border=True */
    /* אנחנו משתמשים בסלקטור הכי אגרסיבי שקיים ב-Streamlit */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 18px !important;
        padding: 22px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
    }

    /* עיצוב הרשומות הפנימיות (פס תכלת אחיד) */
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
        color: #1f2a44 !important;
        text-align: right !important;
    }

    /* יישור לימין לכל רכיבי המערכת */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label, h3, p {
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
    st.error("Missing Data Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()

# --- 4. תצוגת כותרת ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

# --- 5. פרופיל וברכה ---
img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64:
        st.markdown(f'<div class="profile-container"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
with p3:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 6. KPI Section (תיקון "לפי התכנון") ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k_style = "background:white; padding:15px; border-radius:12px; text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.02);"
with k1: st.markdown(f"<div style='{k_style} border-top:4px solid #ff4b4b;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div style='{k_style} border-top:4px solid #ffa500;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div style='{k_style} border-top:4px solid #00c853;'>לפי התכנון 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div style='{k_style}'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 7. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
c_right, c_left = st.columns([2, 1.2])

with c_right:
    # אזור פרויקטים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for i, row in projects.iterrows():
            st.markdown(f'<div class="record-box"><span><b>{row["project_name"]}</b></span><span style="color:gray; font-size:0.85em;">{row.get("project_type", "פרויקט")}</span></div>', unsafe_allow_html=True)

    # אזור AI Oracle
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_proj_final")
        with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_input_final")
        st.button("שגר שאילתה 🚀", use_container_width=True, key="ai_btn_final")

with c_left:
    # אזור פגישות
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for i, r in t_m.iterrows():
                st.markdown(f'<div class="record-box"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    # אזור תזכורות
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        for i, row in t_r.iterrows():
            st.markdown(f'<div class="record-box"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
        
        if st.button("➕ הוסף תזכורת", key="add_rem_now"): st.session_state.add_mode = True
        if st.session_state.get("add_mode"):
            nt = st.text_input("משימה:", key="nt_text_now")
            if st.button("✅ שמור", key="save_rem_now"):
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"reminder_text": nt, "date": today}])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
