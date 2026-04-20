import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ועיצוב (זהה לחלוטין למקור שלך) ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# הוספתי הגדרה קטנה ל-.project-link כדי שנוכל להקליק על פרויקטים
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
    div[data-testid="stVerticalBlockBorderWrapper"], .st-emotion-cache-1ne20ew {
        background: white !important;
        background-color: white !important;
        border: 1.5px solid transparent !important;
        border-radius: 18px !important;
        padding: 15px !important;
    }
    .record-row {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    div[data-testid="stWidgetLabel"] { justify-content: flex-start !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. פונקציות עזר ונתונים (נשאר ללא שינוי) ---
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

# --- 3. ניהול מצב (Session State) ---
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "selected_project_name" not in st.session_state: st.session_state.selected_project_name = None

# --- 4. לוגיקת דפים ---

# פונקציה למעבר לדף פרויקט
def open_project(name):
    st.session_state.selected_project_name = name
    st.session_state.current_page = "project"
    st.rerun()

# פונקציה לחזרה לדף הראשי
def close_project():
    st.session_state.current_page = "main"
    st.session_state.selected_project_name = None
    st.rerun()

# --- דף פרויקט ספציפי ---
if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project_name
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לדשבורד", use_container_width=False):
        close_project()
        
    col_info, col_extra = st.columns([2, 1])
    with col_info:
        with st.container(border=True):
            st.markdown(f"### 📁 פרטי פרויקט: {p_name}")
            st.write("כאן יופיע המידע הכללי על הפרויקט כפי שביקשת.")
            st.info("זהו דף הפרויקט החדש. העיצוב נשמר והיישור לימין מוגדר.")
    with col_extra:
         with st.container(border=True):
            st.markdown("### 📊 סטטוס")
            st.write("סטטוס פרויקט: פעיל")

# --- דף ראשי ---
else:
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
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([2, 1.2])

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            with st.container(height=300, border=False):
                for _, row in projects.iterrows():
                    # שינוי כאן: הפיכת השורה ללחיצה
                    if st.button(f"📂 {row['project_name']}", key=f"p_{row['project_name']}", use_container_width=True):
                        open_project(row['project_name'])

        with st.container(border=True):
            st.markdown('<h3>📋 משימות חדשות באז\'ור</h3>', unsafe_allow_html=True)
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {}); p_name_task = f.get('System.TeamProject', 'General'); t_title = f.get('System.Title', 'ללא כותרת'); t_id = t.get('id')
                    t_url = f"https://dev.azure.com/amandigital/{urllib.parse.quote(p_name_task)}/_workitems/edit/{t_id}"
                    st.markdown(f'<div class="record-row"><div style="flex-grow: 1; text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"><a href="{t_url}" target="_blank" style="color: #0078d4; text-decoration: underline; font-weight: 500; font-size: 0.95em;">🔗 {t_title}</a></div><span class="tag-orange" style="margin-right: 12px; flex-shrink: 0;">{p_name_task}</span></div>', unsafe_allow_html=True)
            else: st.markdown('<p style="text-align: right; color: gray;">אין משימות חדשות.</p>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            a1, a2 = st.columns([1, 2]); sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p"); q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
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
                    s_time = fmt_time(r.get('start_time', ''))
                    e_time = fmt_time(r.get('end_time', ''))
                    time_str = f"{s_time} - {e_time}" if s_time and e_time else ""
                    st.markdown(f'<div class="record-row"><span style="flex-grow:1; text-align:right;">📌 {r["meeting_title"]}</span><span class="time-label">{time_str}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            with st.container(border=False):
                t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
                for _, row in t_r.iterrows():
                    st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)

            if st.session_state.adding_reminder:
                with st.container(border=True):
                    r_col1, r_col2 = st.columns([1, 2])
                    new_proj = r_col1.selectbox("בחר פרויקט", projects["project_name"].tolist() + ["כללי"], label_visibility="collapsed")
                    new_text = r_col2.text_input("תיאור התזכורת", placeholder="מה להזכיר?", label_visibility="collapsed")
                    b_col1, b_col2, b_col3 = st.columns([1, 1, 4])
                    if b_col1.button("✅", key="confirm_new"):
                        if new_text:
                            new_data = pd.DataFrame([{"date": today, "reminder_text": new_text, "project_name": new_proj}])
                            st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_data], ignore_index=True)
                            st.session_state.adding_reminder = False
                            st.rerun()
                    if b_col2.button("❌", key="cancel_new"):
                        st.session_state.adding_reminder = False
                        st.rerun()
            else:
                if st.button("➕", use_container_width=True):
                    st.session_state.adding_reminder = True
                    st.rerun()
