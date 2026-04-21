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
    
    /* הפיכת כפתורי ה-Native לשקופים כדי שה-HTML שלנו יהיה הלחיץ */
    div[data-testid="stButton"] button {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        width: 100% !important;
        box-shadow: none !important;
        color: inherit !important;
    }
    div[data-testid="stButton"] button:hover {
        background: transparent !important;
        border: none !important;
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
        margin-bottom: 5px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
        width: 100%;
        box-sizing: border-box;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .record-row:hover {
        border-color: #4facfe !important;
        background-color: #f8fafc !important;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.15) !important;
        transform: translateY(-1px);
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות ונתונים
# =========================================================

def get_azure_tasks():
    try:
        ORG_NAME = "amandigital"
        auth = ('', st.secrets["AZURE_PAT"])
        wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
        query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New'"}
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    try:
        headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers=headers, timeout=10)
        return res.json().get('items', [])[:5], 200
    except: return [], 500

def get_fathom_summary(recording_id):
    try:
        headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
        res = requests.get(f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary", headers=headers)
        return res.json().get("summary", {}).get("markdown_formatted")
    except: return None

def refine_with_ai(text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"סכם בעברית עסקית:\n{text}").text
    except: return "שגיאה בעיבוד AI"

def fmt_time(t):
    try: return t.strftime("%H:%M")
    except: return ""

# טעינת קבצים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Data Files"); st.stop()

# סשן סטייט
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df

# =========================================================
# 3. ניווט ולוגיקת דפים
# =========================================================
params = st.query_params
selected_proj = params.get("proj")

if selected_proj:
    # --- דף פרויקט ספציפי ---
    st.markdown(f'<h1 class="dashboard-header">{selected_proj}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד הראשי"):
        st.query_params.clear()
        st.rerun()
    
    st.container(border=True).info(f"מידע מפורט עבור פרויקט: {selected_proj}")
    # כאן אפשר להוסיף את ה-Tabs של הפרויקט

else:
    # --- דף ראשי (הדשבורד) ---
    st.markdown('<h1 class="dashboard-header">AI Management Dashboard</h1>', unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        img_b64 = get_base64_image("profile.png")
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3:
        now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
        greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
        st.markdown(f"<div><h3 style='margin-bottom:0;'>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([1, 1])

    with col_right:
        # פרויקטים
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים פעילים")
            for _, row in projects.iterrows():
                name = row['project_name']
                row_html = f'''
                    <div class="record-row">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <b>📂 {name}</b>
                            <span class="tag-blue">{row.get("project_type", "PaaS")}</span>
                        </div>
                        <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span>
                    </div>
                '''
                if st.button(row_html, key=f"p_{name}", unsafe_allow_html=True):
                    st.query_params.proj = name
                    st.rerun()

        # אז'ור
        with st.container(border=True):
            st.markdown("### 📋 משימות Azure")
            for t in get_azure_tasks():
                f = t.get('fields', {})
                st.markdown(f'<div class="record-row"><span>🔗 {f.get("System.Title")}</span><span class="tag-orange">{f.get("System.TeamProject")}</span></div>', unsafe_allow_html=True)

    with col_left:
        # פגישות
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r.get("start_time"))}</span></div>', unsafe_allow_html=True)

        # פאטום (לחיץ)
        with st.container(border=True):
            st.markdown("### ✨ סיכומי Fathom")
            if 'f_mtgs' not in st.session_state:
                st.session_state.f_mtgs, _ = get_fathom_meetings()
            
            for mtg in st.session_state.f_mtgs:
                rid = mtg.get('recording_id')
                t_key, o_key = f"sum_{rid}", f"open_{rid}"
                is_open = st.session_state.get(o_key, False)
                
                f_html = f'''
                    <div class="record-row">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <b>📅 {mtg.get('title')}</b>
                            <span style="color: #94a3b8; font-size: 0.8rem;">{mtg.get('recording_start_time')[:10]}</span>
                        </div>
                        <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">{"expand_more" if is_open else "chevron_left"}</span>
                    </div>
                '''
                if st.button(f_html, key=f"f_{rid}", unsafe_allow_html=True):
                    st.session_state[o_key] = not is_open
                    st.rerun()
                
                if is_open:
                    if t_key in st.session_state:
                        st.info(st.session_state[t_key])
                    elif st.button("צור סיכום AI ✨", key=f"gen_{rid}", use_container_width=True):
                        with st.spinner("מעבד..."):
                            raw = get_fathom_summary(rid)
                            if raw: st.session_state[t_key] = refine_with_ai(raw)
                            st.rerun()

            if st.button("רענן רשימה 🔄", use_container_width=True):
                st.session_state.f_mtgs, _ = get_fathom_meetings()
                st.rerun()
