import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components
import google.generativeai as genai
from streamlit_js_eval import get_geolocation

# =========================================================
# 1. הגדרות דף ועיצוב (CSS)
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* יישור כפתורים בתוך עמודות שיהיו בקו אחד עם תיבות טקסט */
    div[data-testid="column"] button {
        margin-top: 0px !important;
        height: 38px !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }

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
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 18px !important;
        padding: 15px !important;
    }

    .record-row {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 3px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות עזר (ללא שינוי)
# =========================================================
def get_weather_realtime(location):
    if location and 'coords' in location:
        lat, lon = location['coords']['latitude'], location['coords']['longitude']
        try:
            g = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}", headers={'User-Agent': 'SivanDash'}).json()
            city = g.get('address', {}).get('city') or g.get('address', {}).get('town') or "ישראל"
            w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
            temp = round(w['current_weather']['temperature'])
            return f"☀️ {temp}°C", city
        except: pass
    return "☀️ --°C", "ישראל"

def get_azure_tasks():
    ORG_NAME = "amandigital"
    wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject], [System.CreatedDate] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject,System.CreatedDate&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    api_key = st.secrets["FATHOM_API_KEY"]
    url = "https://api.fathom.ai/external/v1/meetings"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200: return response.json().get('items', [])[:5], 200
        return [], response.status_code
    except: return [], 500

def get_fathom_summary(recording_id):
    api_key = st.secrets["FATHOM_API_KEY"]
    url = f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200: return response.json().get("summary", {}).get("markdown_formatted")
        return None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"סכם את הפגישה לעברית עסקית רהוטה:\n\n{raw_text}"
        return model.generate_content(prompt).text
    except: return "שגיאה בסיכום"

def fmt_time(t):
    try: return t.strftime("%H:%M")
    except: return ""

# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files (my_projects, meetings, reminders)"); st.stop()

# =========================================================
# 3. Session State
# =========================================================
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False

# =========================================================
# 4. מבנה התצוגה
# =========================================================
loc = get_geolocation()

if st.session_state.current_page == "project":
    p_name = st.session_state.get("selected_project", "פרויקט")
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.session_state.current_page = "main"
        st.rerun()
    with st.container(border=True):
        st.markdown(f"### ℹ️ ניהול פרויקט: {p_name}")
else:
    # --- דף ראשי ---
    if loc: w_text, w_city = get_weather_realtime(loc)
    else: w_text, w_city = "☀️ --°C", "מזהה מיקום..."
    
    st.markdown(f'<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3:
        st.markdown(f"<div><h3 style='margin-bottom:0;'>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_right, col_left = st.columns([1, 1])

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                st.markdown(f'<div class="record-row"><b>📂 {row["project_name"]}</b><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown('### 📋 משימות חדשות באז\'ור')
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {}); t_title = f.get('System.Title', '')
                    st.markdown(f'<div class="record-row"><span>🔗 {t_title}</span></div>', unsafe_allow_html=True)

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty: st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    st.markdown(f'<div class="record-row">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

        # =========================================================
        # אזור תזכורות (כאן התיקון המרכזי)
        # =========================================================
        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            
            # הצגת תזכורות קיימות
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'''
                    <div class="record-row">
                        <span>🔔 {row["reminder_text"]}</span>
                        <span class="tag-orange">{row.get("project_name", "כללי")}</span>
                    </div>
                ''', unsafe_allow_html=True)

            # שורת הוספה
            if st.session_state.adding_reminder:
                # חלוקה ל-4 עמודות למניעת ירידת שורה
                r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 3, 0.45, 0.45])
                with r_col1:
                    new_proj = st.selectbox("פרויקט", projects["project_name"].tolist() + ["כללי"], label_visibility="collapsed", key="new_rem_proj")
                with r_col2:
                    new_text = st.text_input("תיאור", placeholder="מה להזכיר?", label_visibility="collapsed", key="new_rem_text")
                with r_col3:
                    if st.button("✅", key="save_rem_btn"):
                        if new_text:
                            new_row = {"date": today, "reminder_text": new_text, "project_name": new_proj}
                            st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([new_row])], ignore_index=True)
                            st.session_state.adding_reminder = False
                            st.rerun()
                with r_col4:
                    if st.button("❌", key="cancel_rem_btn"):
                        st.session_state.adding_reminder = False
                        st.rerun()
            else:
                if st.button("➕ הוספת תזכורת", use_container_width=True):
                    st.session_state.adding_reminder = True
                    st.rerun()

        # =========================================================
        # אזור Fathom (מסודר פעם אחת)
        # =========================================================
        with st.container(border=True):
            st.markdown("### ✨ סיכומי פגישות Fathom")
            f_meetings = st.session_state.get('fathom_meetings', [])
            if f_meetings:
                for idx, mtg in enumerate(f_meetings):
                    st.markdown(f'<div class="record-row">📅 {mtg.get("title", "פגישה")}</div>', unsafe_allow_html=True)
            else:
                if st.button("רענן פגישות Fathom 🔄"):
                    items, status = get_fathom_meetings()
                    st.session_state['fathom_meetings'] = items
                    st.rerun()
