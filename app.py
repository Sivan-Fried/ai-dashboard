import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ועיצוב מלוטש ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800;
        margin-bottom: 20px;
    }
    h3 {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
        color: #1f2a44 !important;
        text-align: right !important;
    }
    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }
    .kpi-card {
        background: white !important;
        padding: 15px !important;
        border-radius: 12px !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    
    /* מלבנים לבנים */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 18px !important;
        padding: 15px !important;
    }

    /* עיצוב רשומה - צמצום מרווחים */
    .record-row {
        background: #ffffff !important;
        padding: 12px 15px !important;
        border-radius: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
        margin-bottom: 0px !important; /* ביטול מרווח תחתון של ה-div */
    }
    
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    
    /* תיקון כפתור שקוף על כל הרשומה */
    .project-container {
        position: relative;
        margin-bottom: 8px; /* מרווח בין הרשומות מנוהל כאן */
    }
    .project-container .stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
        cursor: pointer;
        padding: 0 !important;
    }
    .project-container .stButton > button:hover {
        background: rgba(79, 172, 254, 0.05) !important;
    }

    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. פונקציות ונתונים ---
def get_azure_tasks():
    ORG_NAME = "amandigital"
    wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(wiql_url, json=query, auth=auth)
        work_items = res.json().get('workItems', [])
        if not work_items: return []
        ids = ",".join([str(item['id']) for item in work_items[:5]])
        details_res = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&api-version=6.0", auth=auth)
        return details_res.json().get('value', [])
    except: return []

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

# --- 3. ניהול מצב ---
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "selected_project" not in st.session_state: st.session_state.selected_project = None

# --- 4. תצוגה ---
if st.session_state.current_page == "project":
    # --- דף פרויקט ספציפי ---
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    
    # כפתור חזרה מעוצב
    if st.button("⬅️ חזרה לדשבורד הראשי"):
        st.session_state.current_page = "main"
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.container(border=True):
            st.markdown(f"### ℹ️ מידע כללי על {p_name}")
            st.write("כאן נוכל להוסיף את כל המידע הרלוונטי על הפרויקט שבחרת.")
    with c2:
        with st.container(border=True):
            st.markdown("### 📊 מדדים")
            st.write("סטטוס: פעיל")

else:
    # --- דף ראשי ---
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3: st.markdown(f"<div><h3 style='margin-bottom:0;'>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    for i, (label, val) in enumerate([("בסיכון 🔴", "אדום"), ("במעקב 🟡", "צהוב"), ("תקין 🟢", "ירוק"), ("סה\"כ פרויקטים", "all")]):
        with [k1, k2, k3, k4][i]:
            count = len(projects) if val == "all" else len(projects[projects["status"]==val])
            st.markdown(f'<div class="kpi-card">{label}<br><b>{count}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([2, 1.2])

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            with st.container(height=320, border=False):
                for _, row in projects.iterrows():
                    # עטיפת הרשומה ב-container עם Class ייעודי ללחיצה קלה
                    st.markdown(f'<div class="project-container">', unsafe_allow_html=True)
                    with st.container():
                        st.markdown(f'''
                            <div class="record-row">
                                <b>📂 {row["project_name"]}</b>
                                <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                        if st.button("", key=f"btn_{row['project_name']}", use_container_width=True):
                            st.session_state.selected_project = row['project_name']
                            st.session_state.current_page = "project"
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<h3>📋 משימות חדשות באז\'ור</h3>', unsafe_allow_html=True)
            tasks = get_azure_tasks()
            if tasks:
                for t in tasks:
                    f = t.get('fields', {}); t_title = f.get('System.Title', 'ללא כותרת'); t_id = t.get('id')
                    st.markdown(f'<div class="record-row"><div style="text-align:right;">🔗 {t_title}</div><span class="tag-orange">Azure</span></div>', unsafe_allow_html=True)
            else: st.write("אין משימות חדשות")

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            a1, a2 = st.columns([1, 2])
            sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
            q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                if q_in:
                    with st.spinner("מנתח..."): time.sleep(1)
                    st.session_state.ai_response = f"**ניתוח עבור {sel_p}:** הסטטוס תקין."
            if st.session_state.ai_response: st.info(st.session_state.ai_response)

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            # ... (לוגיקת פגישות)
            st.write("אין פגישות היום")

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            if st.button("➕ הוסף תזכורת", use_container_width=True):
                st.session_state.adding_reminder = True
            # ... (שאר לוגיקת תזכורות)
