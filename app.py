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

# --- 2. CSS מוחלט (בלי פשרות) ---
st.html("""
<style>
    /* רקע כללי ויישור לימין */
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* כותרת גרדיאנט */
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 25px !important;
    }

    /* מסגרת גרדיאנט לכל הקונטיינרים - כפייה על האלמנט של Streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2.5px solid transparent !important;
        border-radius: 18px !important;
        padding: 20px !important;
        background-color: white !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    }

    /* עיצוב רשומות - מבנה ה"פס" המקורי */
    .record-row {
        background: #ffffff !important;
        padding: 12px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 6px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
    }

    .project-type-tag {
        color: #4facfe;
        font-size: 0.85em;
        font-weight: 600;
        background: #f0f9ff;
        padding: 2px 10px;
        border-radius: 6px;
    }

    /* יישור טקסט מערכתי */
    h3, p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""")

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files (xlsx)"); st.stop()

# ניהול סטייט לתזכורות
if "rem_live" not in st.session_state:
    df_rem = reminders.copy()
    if 'related_project' not in df_rem.columns: df_rem['related_project'] = "כללי"
    st.session_state.rem_live = df_rem

# --- 4. כותרת ופרופיל ---
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

# --- 5. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # פרויקטים ומרכיבים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            st.markdown(f"""
                <div class="record-row">
                    <span style="font-weight:bold; color:#1f2a44;">📂 {row['project_name']}</span>
                    <span class="project-type-tag">{row.get('project_type', 'פרויקט')}</span>
                </div>
            """, unsafe_allow_html=True)

    # AI Oracle
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
        st.button("שגר שאילתה 🚀", key="ai_btn", use_container_width=True)

with col_left:
    # פגישות היום
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    # תזכורות
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        
        for _, row in t_r.iterrows():
            p_tag = row.get('related_project', 'כללי')
            st.markdown(f"""
                <div class="record-row">
                    <span>🔔 {row['reminder_text']}</span>
                    <span class="project-type-tag" style="background:#fef3c7; color:#d97706;">{p_tag}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("➕ הוסף תזכורת", key="add_r"):
            st.session_state.add_mode = True
        
        if st.session_state.get("add_mode"):
            with st.form("reminder_form"):
                nt = st.text_input("מה המשימה?")
                np = st.selectbox("שיוך לפרויקט:", ["כללי"] + projects["project_name"].tolist())
                if st.form_submit_button("✅ שמור"):
                    if nt:
                        new_row = pd.DataFrame([{"reminder_text": nt, "date": today, "related_project": np}])
                        st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_row], ignore_index=True)
                        st.session_state.add_mode = False
                        st.rerun()
