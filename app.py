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

# --- 2. CSS אבסולוטי לעיצוב הרשומות והמסגרות ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 25px !important;
    }

    /* מסגרת גרדיאנט לקונטיינרים */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2.5px solid transparent !important;
        border-radius: 18px !important;
        padding: 20px !important;
        background-color: white !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    }

    /* עיצוב רשומות - שם מימין, תגית משמאל */
    .record-row {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 6px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
    }

    .project-tag {
        color: #4facfe;
        font-size: 0.8em;
        font-weight: 600;
        background: #f0f9ff;
        padding: 2px 8px;
        border-radius: 5px;
    }

    /* תיקון יישור לכל הממשק */
    h3, p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    
    /* הוספת תזכורת בשורה אחת */
    .inline-form { display: flex; gap: 10px; align-items: flex-end; }
</style>
""", unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx") # וודאי שיש כאן עמודה בשם 'project' או 'related_project'
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"Error loading files: {e}"); st.stop()

if "rem_live" not in st.session_state:
    st.session_state.rem_live = reminders.copy()

# --- 4. תצוגה עליונה ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" style="width:130px; height:130px; border-radius:50%; object-fit: cover; object-position: center 20%; border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.1);"></div>', unsafe_allow_html=True)
with p3:
    st.markdown(f"<div><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. דשבורד מרכזי ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # פרויקטים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            st.markdown(f"""
                <div class="record-row">
                    <span style="font-weight:bold;">📂 {row['project_name']}</span>
                    <span class="project-tag">{row.get('project_type', 'פרויקט')}</span>
                </div>
            """, unsafe_allow_html=True)

    # AI Oracle
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
        st.button("שגר שאילתה 🚀", key="ai_btn", use_container_width=True)

with col_left:
    # פגישות
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    # תזכורות עם שם פרויקט אמיתי
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        
        for _, row in t_r.iterrows():
            # מנסה לקחת את שם הפרויקט מהעמודה המתאימה בקובץ reminders.xlsx
            p_name = row.get('project', row.get('related_project', 'כללי'))
            st.markdown(f"""
                <div class="record-row">
                    <span>🔔 {row['reminder_text']}</span>
                    <span class="project-tag" style="background:#fef3c7; color:#d97706;">{p_name}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # הוספה בשורה אחת
        with st.expander("➕ הוסף תזכורת מהירה", expanded=False):
            c1, c2, c3 = st.columns([2, 1, 0.5])
            with c1: nt = st.text_input("משימה", label_visibility="collapsed", placeholder="מה עושים?", key="new_t")
            with c2: np = st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="new_p")
            with c3: save = st.button("✅", key="save_t")
            
            if save and nt:
                new_data = pd.DataFrame([{"reminder_text": nt, "date": today, "project": np}])
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_data], ignore_index=True)
                st.rerun()
