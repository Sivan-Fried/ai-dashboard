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
        font-size: 2.8rem !important;
        font-weight: 800;
        margin-top: -20px;
        margin-bottom: 10px;
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

    /* תיקון כפתורי Fathom */
    .fathom-container {
        position: relative;
        margin-bottom: 5px;
    }
    .fathom-row-ui {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        border: 1px solid #edf2f7;
        border-right: 5px solid #4facfe;
        border-radius: 8px;
        padding: 10px 15px;
        direction: rtl;
    }
    .stButton > button[key^="f_trig"] {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
    }

    .fathom-pill-v2 {
        background-color: #f1f5f9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        margin-right: 10px;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    p, span, label { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות ונתונים
# =========================================================

def get_weather():
    try:
        geo = requests.get('https://ipapi.co/json/', timeout=3).json()
        # תרגום בסיסי לעברית
        city_en = geo.get('city', 'Israel')
        cities_map = {"Holon": "חולון", "Tel Aviv": "תל אביב", "Petah Tikva": "פתח תקווה", "Rishon LeZiyyon": "ראשון לציון", "Jerusalem": "ירושלים"}
        city = cities_map.get(city_en, city_en)
        
        lat, lon = geo.get('latitude', 32.08), geo.get('longitude', 34.88)
        w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=3).json()
        curr = w_res.get('current_weather', {})
        temp = round(curr.get('temperature', 22))
        icon = "☀️" if curr.get('weathercode', 0) == 0 else "☁️" if curr.get('weathercode', 0) < 50 else "🌧️"
        return f"{icon} {temp}°C", city
    except:
        return "☀️ 22°C", "ישראל"

# (יתר הפונקציות Azure, Fathom, AI נשארות ללא שינוי מהקוד הקודם שלך)
def get_azure_tasks():
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post("https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", json={"query": "SELECT [System.Id], [System.Title], [System.TeamProject], [System.CreatedDate] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/amandigital/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject,System.CreatedDate&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]}, timeout=15)
        return (res.json().get('items', [])[:5], 200) if res.status_code == 200 else ([], res.status_code)
    except: return [], 500

def get_fathom_summary(rid):
    try:
        res = requests.get(f"https://api.fathom.ai/external/v1/recordings/{rid}/summary", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]}, timeout=15)
        return res.json().get("summary", {}).get("markdown_formatted") if res.status_code == 200 else None
    except: return None

def refine_with_ai(txt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"סכם את הפגישה לעברית עסקית רהוטה. מבנה: נושא, תקציר מנהלים, החלטות מרכזיות ומשימות:\n\n{txt}").text
    except Exception as e: return f"שגיאה: {e}"

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

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False

# =========================================================
# 3. תצוגת דף ראשי
# =========================================================

# כותרת ראשית מעל הכל
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

# שורת Header: מזג אוויר משמאל | תמונה וברכה במרכז
h_left, h_center, h_right = st.columns([1, 1.5, 1])

with h_left:
    w_info, city_name = get_weather()
    st.markdown(f"""
        <div style="background: white; padding: 10px; border-radius: 15px; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; 
                    margin-top: 15px; border: 1px solid #edf2f7; width: 130px;">
            <span style="font-size: 0.75rem; color: #4facfe; font-weight: 700; display: block;">{city_name}</span>
            <b style="font-size: 1.1rem; color: #1f2a44;">{w_info}</b>
        </div>
    """, unsafe_allow_html=True)

with h_center:
    img_b64 = get_base64_image("profile.png")
    if img_b64:
        st.markdown(f'<div style="display:flex; flex-direction:column; align-items:center;">'
                    f'<img src="data:image/png;base64,{img_b64}" class="profile-img">'
                    f'</div>', unsafe_allow_html=True)
    
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
    st.markdown(f"<p style='text-align: center; color: #1f2a44; font-weight: 700; font-size: 1.2rem; margin-top: 10px;'>{greeting}, סיון!</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray; margin-top: -15px; font-size: 0.9rem;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>", unsafe_allow_html=True)

# --- KPIs ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- גוף הדשבורד ---
col_right, col_left = st.columns([1, 1])

with col_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים")
        with st.container(height=300, border=False):
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'''<a href="{p_url}" target="_self" class="project-link"><div class="record-row">
                    <div style="display: flex; align-items: center; gap: 10px;"><b>📂 {row["project_name"]}</b><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div>
                    <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span></div></a>''', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('### 📋 משימות חדשות באז\'ור')
        tasks = get_azure_tasks()
        if tasks:
            for t in tasks:
                f = t.get('fields', {}); t_title = f.get('System.Title', ''); p_task = f.get('System.TeamProject', 'General')
                st.markdown(f'<div class="record-row"><span>🔗 {t_title[:40]}...</span><span class="tag-orange">{p_task}</span></div>', unsafe_allow_html=True)
        else: st.write("אין משימות חדשות")

with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r.get("start_time"))}</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        col_t, col_ref = st.columns([0.85, 0.15])
        with col_t: st.markdown("### ✨ סיכומי פגישות Fathom")
        with col_ref: 
            if st.button("🔄", key="ref_f"): st.rerun()

        f_mtgs = st.session_state.get('fathom_meetings')
        if not f_mtgs:
            f_mtgs, _ = get_fathom_meetings()
            st.session_state['fathom_meetings'] = f_mtgs

        for idx, mtg in enumerate(f_mtgs):
            rid, title = mtg.get('recording_id'), mtg.get('title') or "פגישה"
            date_s = mtg.get('recording_start_time', '')[:10]
            okey = f"open_{rid}"
            is_open = st.session_state.get(okey, False)
            
            st.markdown(f'''<div class="fathom-container"><div class="fathom-row-ui">
                <div style="display:flex; align-items:center;"><span style="font-size:1.1rem; margin-left:10px;">📅</span>
                <span style="font-weight:600; font-size:0.85rem;">{title}</span><span class="fathom-pill-v2">{date_s}</span></div>
                <span class="material-symbols-rounded" style="color:#94a3b8;">{"expand_more" if is_open else "chevron_left"}</span></div></div>''', unsafe_allow_html=True)
            
            if st.button("", key=f"f_trig_{rid}_{idx}", use_container_width=True):
                st.session_state[okey] = not is_open; st.rerun()
            
            if is_open:
                s_key = f"sum_{rid}"
                if s_key not in st.session_state:
                    if st.button("צור סיכום עם AI 🪄", key=f"gen_{rid}"):
                        with st.spinner("מנתח..."):
                            raw = get_fathom_summary(rid)
                            if raw: st.session_state[s_key] = refine_with_ai(raw); st.rerun()
                else: st.info(st.session_state[s_key])
