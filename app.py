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

# --- 2. CSS מינימליסטי ויציב - יישור לימין וגלילה ---
st.markdown("""
<style>
    /* הגדרות כלליות */
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; text-align: right !important; }
    
    /* כותרת */
    .dashboard-header {
        color: #1e3a8a;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800;
        margin-bottom: 20px;
    }

    /* תמונת פרופיל */
    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }

    /* KPI - לבן, נקי, בלי בורדר */
    .kpi-card {
        background: white !important;
        padding: 15px !important;
        border-radius: 12px !important;
        text-align: center !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* מסגרות קונטיינרים */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #e2e8f0 !important;
        border-right: 5px solid #4facfe !important;
        border-radius: 15px !important;
    }

    /* אזור גלילה קשיח לתזכורות ופרויקטים */
    .scroll-area {
        max-height: 300px;
        overflow-y: auto;
        direction: rtl;
        padding-left: 10px;
    }

    /* שורה ברשימה */
    .item-row {
        background: #f8fafc;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* יישור פקדים */
    h3, p, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    div[data-testid="stWidgetLabel"] { justify-content: flex-start !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()
if "ai_msg" not in st.session_state: st.session_state.ai_msg = ""

# --- 4. כותרת ופרופיל ---
st.markdown('<h1 class="dashboard-header">דשבורד ניהול</h1>', unsafe_allow_html=True)
p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    img = get_base64_image("profile.png")
    if img: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img}" class="profile-img"></div>', unsafe_allow_html=True)
with p3:
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    st.markdown(f"<div><h3>שלום סיון,</h3><p>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

# --- 6. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים")
        # שימוש ב-HTML פשוט בתוך המכולה כדי להבטיח גלילה
        proj_list = "".join([f'<div class="item-row"><span>📂 {r["project_name"]}</span></div>' for _, r in projects.iterrows()])
        st.components.v1.html(f'<div class="scroll-area">{proj_list}</div>', height=300)

    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_sel")
        q_in = st.text_input("שאלה", key="q_in")
        if st.button("שגר שאילתה 🚀", use_container_width=True):
            st.session_state.ai_msg = f"ניתוח עבור {sel_p}: הפרויקט בסטטוס תקין."
        if st.session_state.ai_msg:
            st.info(st.session_state.ai_msg)

with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        for _, r in t_m.iterrows():
            st.markdown(f'<div class="item-row">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        rem_list = "".join([f'<div class="item-row"><span>🔔 {r["reminder_text"]}</span></div>' for _, r in t_r.iterrows()])
        st.components.v1.html(f'<div class="scroll-area">{rem_list}</div>', height=250)
        
        # הוספה פשוטה
        if st.button("➕ הוסף תזכורת", use_container_width=True):
            st.info("כאן נפתח טופס ההוספה - לחצי שוב כדי לרענן")
