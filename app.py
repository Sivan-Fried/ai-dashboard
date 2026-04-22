import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
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
    
    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }
    
    .kpi-card {
        background: white !important; padding: 15px !important; border-radius: 12px !important;
        text-align: center !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    
    .record-row {
        background: #ffffff !important; padding: 10px 15px !important; border-radius: 10px !important;
        margin-bottom: 3px !important; border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important; display: flex !important;
        justify-content: space-between !important; align-items: center !important;
    }

    /* תיקון כפתורי פאטום שקופים */
    .fathom-wrapper { position: relative; margin-bottom: 4px; }
    .fathom-row-ui {
        display: grid; grid-template-columns: auto 1fr auto; align-items: center;
        background: white; border: 1px solid #edf2f7; border-right: 5px solid #4facfe;
        border-radius: 8px; padding: 0 16px; height: 45px; direction: rtl;
    }
    .stButton > button[key^="f_trig"] {
        position: absolute; top: 0; left: 0; width: 100%; height: 45px;
        background: transparent !important; border: none !important; color: transparent !important; z-index: 10;
    }

    .fathom-pill-v2 { background-color: #f1f5f9; color: #475569; padding: 1px 8px; border-radius: 10px; font-size: 0.75rem; margin-right: 12px; }
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    p, span, label, h3 { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. לוגיקה
# =========================================================

def get_weather():
    try:
        geo = requests.get('https://ipapi.co/json/', timeout=3).json()
        city_en = geo.get('city', 'Israel')
        cities_he = {"Holon": "חולון", "Tel Aviv": "תל אביב", "Petah Tikva": "פתח תקווה", "Jerusalem": "ירושלים"}
        city_he = cities_he.get(city_en, city_en)
        lat, lon = geo.get('latitude', 32.08), geo.get('longitude', 34.88)
        w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=3).json()
        curr = w_res.get('current_weather', {})
        temp = round(curr.get('temperature', 22))
        icon = "☀️" if curr.get('weathercode', 0) == 0 else "☁️" if curr.get('weathercode', 0) < 50 else "🌧️"
        return f"{icon} {temp}°C", city_he
    except: return "☀️ 22°C", "ישראל"

def get_azure_tasks():
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post("https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", json={"query": "SELECT [System.Id], [System.Title], [System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        return requests.get(f"https://dev.azure.com/amandigital/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject&api-version=6.0", auth=auth).json().get('value', [])
    except: return []

def get_fathom_meetings():
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]}, timeout=10)
        return res.json().get('items', [])[:5] if res.status_code == 200 else []
    except: return []

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except: st.stop()

if "ai_response" not in st.session_state: st.session_state.ai_response = ""

# =========================================================
# 3. UI - HEADER
# =========================================================

st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

# מבנה עמודות: ימין (ריק) | מרכז (פרופיל) | שמאל (מזג אוויר)
# בגלל RTL, העמודה הראשונה בקוד היא הימנית ביותר במסך.
col_right_spacer, col_center_profile, col_left_weather = st.columns([1, 1, 1])

with col_center_profile:
    img_b64 = get_base64_image("profile.png")
    if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
    st.markdown(f"<p style='text-align:center !important; font-weight:700; font-size:1.1rem; margin-top:10px;'>{greeting}, סיון!</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center !important; color:gray; margin-top:-15px;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>", unsafe_allow_html=True)

with col_left_weather:
    w_info, city_name = get_weather()
    st.markdown(f"""
        <div style="background: white; padding: 10px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; border: 1px solid #edf2f7; width: 120px; float: left;">
            <span style="font-size: 0.75rem; color: #4facfe; font-weight: 700; display: block;">{city_name}</span>
            <b style="font-size: 1.1rem; color: #1f2a44;">{w_info}</b>
        </div>
    """, unsafe_allow_html=True)

# KPIs
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# גוף הדשבורד
col_main_right, col_main_left = st.columns([1, 1])

with col_main_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים")
        for _, row in projects.iterrows():
            st.markdown(f'<div class="record-row"><b>📂 {row["project_name"]}</b><span class="material-symbols-rounded" style="color: #94a3b8;">chevron_left</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('### 📋 משימות Azure')
        tasks = get_azure_tasks()
        for t in tasks:
            f = t.get('fields', {})
            st.markdown(f'<div class="record-row"><span>🔗 {f.get("System.Title")[:40]}...</span><span class="tag-orange">{f.get("System.TeamProject")}</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### ✨ עוזר AI אישי")
        a1, a2 = st.columns([1, 2])
        sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed")
        q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed")
        if st.button("שגר שאילתה 🚀", use_container_width=True):
            st.session_state.ai_response = f"ניתוח עבור {sel_p}: הסטטוס תקין."
        if st.session_state.ai_response: st.info(st.session_state.ai_response)

with col_main_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        for _, r in t_m.iterrows():
            st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span style="font-family:monospace;">{r.get("start_time")}</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 📝 סיכומי פגישות Fathom")
        f_mtgs = get_fathom_meetings()
        for idx, mtg in enumerate(f_mtgs):
            rid = mtg.get('recording_id')
            title = mtg.get('title') or "פגישה"
            date_s = mtg.get('recording_start_time', '')[:10]
            okey = f"open_{rid}"
            is_open = st.session_state.get(okey, False)
            
            st.markdown(f'''<div class="fathom-wrapper">
                <div class="fathom-row-ui">
                    <div>📅 {title} <span class="fathom-pill-v2">{date_s}</span></div><div></div>
                    <span class="material-symbols-rounded">{"expand_more" if is_open else "chevron_left"}</span>
                </div>
            </div>''', unsafe_allow_html=True)
            if st.button("", key=f"f_trig_{rid}_{idx}", use_container_width=True):
                st.session_state[okey] = not is_open; st.rerun()
            if is_open: st.info("כאן יופיע הסיכון/סיכום...")
