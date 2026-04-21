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
        border: 1.5px solid transparent !important;
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
# 2. פונקציות ונתונים
# =========================================================

def get_azure_tasks():
    ORG_NAME = "amandigital"
    wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&api-version=6.0", auth=auth)
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
        return response.json().get("summary", {}).get("markdown_formatted") if response.status_code == 200 else None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"סכם את הפגישה לעברית עסקית:\n\n{raw_text}"
        return model.generate_content(prompt).text
    except Exception as e: return f"Error: {e}"

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

# =========================================================
# 3. ניהול ניווט וסטייט
# =========================================================
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "current_page" not in st.session_state: st.session_state.current_page = "main"

params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

# =========================================================
# 4. תצוגת דפים
# =========================================================

if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear()
        st.session_state.current_page = "main"
        st.rerun()
    
    with st.container(border=True):
        st.markdown(f"### ניהול פרויקט: {p_name}")
        if "אלטשולר" in p_name:
            roadmap_html = """<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="utf-8"><style>body { font-family: sans-serif; background: white; margin:0; }.timeline { display:flex; justify-content: space-around; align-items: center; height: 200px; border-bottom: 1px solid #ccc; }</style></head><body><div class="timeline"><div>08.03 LIVE</div><div>24.03 LIVE</div><div>10.04 LIVE</div><div>יולי WIP</div></div></body></html>"""
            components.html(roadmap_html, height=250)
        else: st.info("פרטי פרויקט יוצגו כאן.")

else:
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        img_b64 = get_base64_image("profile.png")
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3:
        now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
        greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
        st.markdown(f"<div><h3>{greeting}, סיון!</h3><p>{now.strftime('%d/%m/%Y')}</p></div>", unsafe_allow_html=True)

    col_right, col_left = st.columns([1, 1])

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_name = row['project_name']
                if st.button(f"📂 {p_name}", key=f"btn_{p_name}", use_container_width=True):
                    st.query_params.proj = p_name
                    st.rerun()

        with st.container(border=True):
            st.markdown("### 📋 משימות Azure")
            for t in get_azure_tasks():
                f = t.get('fields', {})
                st.markdown(f'<div class="record-row"><span>🔗 {f.get("System.Title")}</span><span class="tag-orange">{f.get("System.TeamProject")}</span></div>', unsafe_allow_html=True)

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r.get("start_time"))}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ סיכומי Fathom")
            if 'f_mtgs' not in st.session_state:
                st.session_state.f_mtgs, _ = get_fathom_meetings()
            
            for mtg in st.session_state.f_mtgs:
                rid = mtg.get('recording_id')
                st.markdown(f'<div class="record-row"><b>📅 {mtg.get("title")}</b><span>{mtg.get("recording_start_time")[:10]}</span></div>', unsafe_allow_html=True)
                if st.button("פרטים וסיכום", key=f"f_{rid}", use_container_width=True):
                    with st.spinner("טוען..."):
                        raw = get_fathom_summary(rid)
                        if raw: st.info(refine_with_ai(raw))
