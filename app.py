import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ועיצוב ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

# ייבוא האייקונים של גוגל
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />', unsafe_allow_html=True)

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
    
    /* עיצוב המלבנים הלבנים שתואם למקור שלך */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 18px !important;
        padding: 15px !important;
    }

    /* עיצוב שורת פרויקט עם החץ החדש */
    .project-row {
        background: #ffffff !important;
        padding: 12px 15px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .project-row:hover {
        background-color: #f8fafc !important;
        border-color: #4facfe !important;
    }

    .arrow-container {
        width: 35px; height: 35px;
        border-radius: 50%;
        background-color: #f8fafc;
        display: flex; align-items: center; justify-content: center;
        color: #94a3b8;
        transition: all 0.3s ease;
    }

    .project-row:hover .arrow-container {
        background-color: #ecfeff;
        color: #0891b2;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }

    /* כפתור שקוף שיושב על כל השורה */
    .stButton > button {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: transparent !important; border: none !important; color: transparent !important;
        z-index: 10; cursor: pointer;
    }
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

def fmt_time(t):
    try: return t.strftime("%H:%M")
    except: return ""

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

# --- 3. ניהול ניווט ---
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "selected_project" not in st.session_state: st.session_state.selected_project = None

# --- 4. תצוגה ---

if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.session_state.current_page = "main"; st.rerun()
    with st.container(border=True):
        st.markdown(f"### ℹ️ מידע כללי על {p_name}")
        st.write("כאן יופיע פירוט הפרויקט.")

else:
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    
    # אזור פרופיל
    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3: st.markdown(f"<div><h3 style='margin-bottom:0;'>שלום, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([2, 1.2])

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            with st.container(height=350, border=False):
                for _, row in projects.iterrows():
                    # המבנה החדש שביקשת עם החץ בצד שמאל
                    st.markdown(f'''
                        <div class="project-row">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <b>📂 {row["project_name"]}</b>
                                <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                            </div>
                            <div class="arrow-container">
                                <span class="material-symbols-rounded">chevron_left</span>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                    # כפתור שקוף מעל כל השורה
                    if st.button("", key=f"btn_{row['project_name']}", use_container_width=True):
                        st.session_state.selected_project = row['project_name']
                        st.session_state.current_page = "project"; st.rerun()

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            a1, a2 = st.columns([1, 2])
            sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), key="ai_p", label_visibility="collapsed")
            q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", key="ai_i", label_visibility="collapsed")
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                if q_in:
                    with st.spinner("מנתח..."): time.sleep(1)
                    st.session_state.ai_response = f"**ניתוח עבור {sel_p}:** הסטטוס תקין."
            if st.session_state.ai_response: st.info(st.session_state.ai_response)

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty: st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r.get("start_time"))}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)
            if st.button("➕", use_container_width=True):
                st.session_state.adding_reminder = True
