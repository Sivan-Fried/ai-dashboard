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
    
    /* הפיכת כפתורי ה-Native לשקופים עבור רשימות לחיצות */
    div[data-testid="stButton"] button[kind="secondary"]:has(div.record-row) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        width: 100% !important;
        box-shadow: none !important;
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
        width: 100%;
        transition: all 0.2s ease;
    }
    
    .record-row:hover {
        border-color: #4facfe !important;
        background-color: #f8fafc !important;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.15) !important;
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
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers=headers, timeout=15)
        return res.json().get('items', [])[:5], res.status_code
    except: return [], 500

def get_fathom_summary(recording_id):
    api_key = st.secrets["FATHOM_API_KEY"]
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        res = requests.get(f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary", headers=headers)
        return res.json().get("summary", {}).get("markdown_formatted") if res.status_code == 200 else None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"סכם לעברית עסקית רהוטה עם משימות לביצוע:\n\n{raw_text}").text
    except: return "שגיאה בעיבוד AI"

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
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False
if "current_page" not in st.session_state: st.session_state.current_page = "main"

params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

# =========================================================
# 4. דף פרויקט
# =========================================================
if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear()
        st.session_state.current_page = "main"
        st.rerun()
    
    with st.container(border=True):
        tab_work, tab_res, tab_info = st.tabs(["📅 תוכנית עבודה", "👥 משאבים", "📊 מידע כללי"])
        with tab_work:
            if "אלטשולר" in p_name:
                roadmap_html = """<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap" rel="stylesheet"><style>body { font-family: 'Assistant', sans-serif; background-color: white; margin: 0; padding: 0; overflow: hidden; }.timeline-wrapper { position: relative; width: 1000px; margin: 50px auto; height: 200px; display: flex; justify-content: space-between; align-items: flex-end; padding: 0 50px; }.main-line { position: absolute; bottom: 6px; left: 0; right: 0; height: 1px; background: #cbd5e1; z-index: 1; }.today-indicator { position: absolute; bottom: -15px; right: 525px; display: flex; flex-direction: column; align-items: center; z-index: 5; }.today-line { width: 2px; height: 60px; border-left: 2px dashed #bfdbfe; }.today-text { color: #3b82f6; font-size: 11px; font-weight: 700; margin-bottom: 4px; }.item { display: flex; flex-direction: column; align-items: center; width: 90px; z-index: 3; position: relative; }.card { background: white; padding: 4px 6px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; text-align: center; width: 100%; margin-bottom: 8px; }.connector { width: 1px; height: 15px; background: #e2e8f0; }.dot { width: 12px; height: 12px; background: #475569; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 1px #475569; z-index: 4; }.tag { font-size: 8px; font-weight: 700; padding: 1px 4px; border-radius: 2px; display: inline-block; margin-bottom: 2px; }.amit { background: #eff6ff; color: #1e40af; }.measy { background: #f5f3ff; color: #5b21b6; }.soch { background: #ecfdf5; color: #065f46; }.date { font-size: 13px; font-weight: 600; color: #1e293b; margin: 0; }.status { font-size: 8px; font-weight: 700; margin-top: 2px; }.live { color: #10b981; } .wip { color: #f59e0b; }</style></head><body><div class="timeline-wrapper"><div class="main-line"></div><div class="today-indicator"><span class="today-text">היום 20.04</span><div class="today-line"></div></div><div class="item"><div class="card"><span class="tag amit">עמיתים</span><div class="date">08.03</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag measy">מעסיקים</span><div class="date">08.03</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag soch">סוכנים</span><div class="date">24.03</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag amit">עמיתים</span><div class="date">10.04</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag amit">עמיתים</span><div class="date">יולי</div><span class="status wip">WIP</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag measy">מעסיקים</span><div class="date">TBD</div><span class="status" style="color:#94a3b8">HOLD</span></div><div class="connector"></div><div class="dot"></div></div></div></body></html>"""
                components.html(roadmap_html, height=300)
            else: st.info(f"מידע עבור {p_name}")

# =========================================================
# 5. דף ראשי
# =========================================================
else:
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
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_name = row['project_name']
                row_html = f'<div class="record-row"><div style="display:flex;align-items:center;gap:10px;"><b>📂 {p_name}</b><span class="tag-blue">{row.get("project_type","")}</span></div><span class="material-symbols-rounded" style="color:#94a3b8;font-size:20px;">chevron_left</span></div>'
                if st.button(row_html, key=f"p_{p_name}", unsafe_allow_html=True):
                    st.query_params.proj = p_name
                    st.rerun()

        with st.container(border=True):
            st.markdown("### 📋 משימות Azure")
            for t in get_azure_tasks():
                f = t.get('fields', {})
                st.markdown(f'<div class="record-row"><span>🔗 {f.get("System.Title")}</span><span class="tag-orange">{f.get("System.TeamProject")}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI")
            a1, a2 = st.columns([1, 2]); sel_p = a1.selectbox("בחר", projects["project_name"].tolist(), label_visibility="collapsed"); q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed")
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                st.session_state.ai_response = f"ניתוח עבור {sel_p}: הסטטוס תקין."
            if st.session_state.ai_response: st.info(st.session_state.ai_response)

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r.get("start_time"))}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)
            if st.button("➕", use_container_width=True): st.session_state.adding_reminder = True; st.rerun()

        # --- אזור Fathom (השורה לחיצה) ---
        with st.container(border=True):
            st.markdown("### ✨ סיכומי Fathom")
            if 'f_mtgs' not in st.session_state:
                st.session_state.f_mtgs, _ = get_fathom_meetings()
            
            for mtg in st.session_state.f_mtgs:
                rid = mtg.get('recording_id')
                o_key, s_key = f"open_{rid}", f"sum_{rid}"
                is_open = st.session_state.get(o_key, False)
                
                f_html = f'<div class="record-row"><div style="display:flex;align-items:center;gap:10px;"><b>📅 {mtg.get("title")}</b><span style="color:#94a3b8;font-size:0.85rem;">{mtg.get("recording_start_time")[:10]}</span></div><span class="material-symbols-rounded" style="color:#94a3b8;font-size:20px;">{"expand_more" if is_open else "chevron_left"}</span></div>'
                
                if st.button(f_html, key=f"f_{rid}", unsafe_allow_html=True):
                    st.session_state[o_key] = not is_open
                    st.rerun()
                
                if is_open:
                    if s_key in st.session_state:
                        st.info(st.session_state[s_key])
                        if st.button("נקה 🗑️", key=f"c_{rid}"): del st.session_state[s_key]; st.rerun()
                    elif st.button("צור סיכום AI ✨", key=f"g_{rid}", use_container_width=True):
                        with st.spinner("מעבד..."):
                            raw = get_fathom_summary(rid)
                            if raw: st.session_state[s_key] = refine_with_ai(raw)
                            st.rerun()
