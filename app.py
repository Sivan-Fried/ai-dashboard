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
    
    /* כותרת מרכזית */
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 3rem !important;
        font-weight: 800;
        margin-bottom: 5px !important;
        padding-top: 20px;
    }

    /* מזג אוויר צף בצד שמאל */
    .weather-floating {
        position: absolute;
        top: 20px;
        left: 20px;
        background: white;
        padding: 10px 15px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
        text-align: center;
        z-index: 100;
        min-width: 100px;
    }

    .profile-img {
        width: 140px; height: 140px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        margin-bottom: 10px;
    }

    .kpi-card {
        background: white !important; padding: 15px !important;
        border-radius: 12px !important; text-align: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    
    .record-row {
        background: #ffffff !important; padding: 10px 15px !important;
        border-radius: 10px !important; margin-bottom: 3px !important;
        border: 1px solid #edf2f7 !important; border-right: 5px solid #4facfe !important;
        display: flex !important; justify-content: space-between !important;
        align-items: center !important; direction: rtl !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    p, span, label { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות לוגיקה
# =========================================================

def get_weather():
    try:
        geo = requests.get('https://ipapi.co/json/', timeout=3).json()
        city_en = geo.get('city', 'Israel')
        # מילון תרגום בסיסי
        cities_he = {"Holon": "חולון", "Tel Aviv": "תל אביב", "Petah Tikva": "פתח תקווה", "Jerusalem": "ירושלים", "Haifa": "חיפה"}
        city_he = cities_he.get(city_en, city_en)
        
        lat, lon = geo.get('latitude', 32.08), geo.get('longitude', 34.88)
        w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=3).json()
        curr = w_res.get('current_weather', {})
        temp = round(curr.get('temperature', 22))
        icon = "☀️" if curr.get('weathercode', 0) == 0 else "☁️" if curr.get('weathercode', 0) < 50 else "🌧️"
        return f"{icon} {temp}°C", city_he
    except:
        return "☀️ 22°C", "ישראל"

def get_azure_tasks():
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post("https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", json={"query": "SELECT [System.Id], [System.Title], [System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New'"}, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        return requests.get(f"https://dev.azure.com/amandigital/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject&api-version=6.0", auth=auth).json().get('value', [])
    except: return []

def get_fathom_meetings():
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]}, timeout=10)
        return res.json().get('items', [])[:5] if res.status_code == 200 else []
    except: return []

def get_fathom_summary(rid):
    try:
        res = requests.get(f"https://api.fathom.ai/external/v1/recordings/{rid}/summary", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]}, timeout=10)
        return res.json().get("summary", {}).get("markdown_formatted") if res.status_code == 200 else None
    except: return None

def refine_with_ai(txt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"סכם לעברית עסקית:\n\n{txt}").text
    except: return "שגיאה בניתוח ה-AI"

# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

# =========================================================
# 3. מבנה הדף (UI)
# =========================================================

# --- HEADER (החלק העליון) ---
w_info, city_name = get_weather()
st.markdown(f"""
    <div class="weather-floating">
        <span style="color: #4facfe; font-weight: 700; font-size: 0.8rem; display:block;">{city_name}</span>
        <b style="font-size: 1.2rem; color: #1f2a44;">{w_info}</b>
    </div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

# תמונה וברכה במרכז מושלם
img_b64 = get_base64_image("profile.png")
col_img_1, col_img_2, col_img_3 = st.columns([1, 1, 1])
with col_img_2:
    if img_b64:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
    st.markdown(f"<div style='text-align:center;'><p style='font-weight:700; font-size:1.3rem; margin-bottom:0;'>{greeting}, סיון!</p>"
                f"<p style='color:gray; font-size:0.9rem;'>{now.strftime('%H:%M | %d/%m/%Y')}</p></div>", unsafe_allow_html=True)

# --- KPIs ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- גוף הדף (עמודות) ---
col_r, col_l = st.columns([1, 1])

with col_r:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים")
        for _, row in projects.iterrows():
            st.markdown(f'''<div class="record-row">
                <div style="display:flex; align-items:center; gap:10px;"><b>📂 {row["project_name"]}</b><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div>
                <span class="material-symbols-rounded" style="color:#94a3b8;">chevron_left</span></div>''', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 📋 משימות Azure")
        tasks = get_azure_tasks()
        if tasks:
            for t in tasks:
                f = t.get('fields', {})
                st.markdown(f'<div class="record-row"><span>🔗 {f.get("System.Title")[:40]}...</span><span class="tag-orange">{f.get("System.TeamProject")}</span></div>', unsafe_allow_html=True)
        else: st.write("אין משימות חדשות")

with col_l:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        for _, r in t_m.iterrows():
            st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span style="color:#64748b; font-family:monospace;">{r.get("start_time")}</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### ✨ סיכומי Fathom")
        f_mtgs = get_fathom_meetings()
        if f_mtgs:
            for mtg in f_mtgs:
                rid = mtg.get('recording_id')
                title = mtg.get('title') or "פגישה"
                date_s = mtg.get('recording_start_time', '')[:10]
                
                with st.expander(f"📅 {title} | {date_s}"):
                    s_key = f"sum_{rid}"
                    if s_key not in st.session_state:
                        if st.button("סכם עם AI 🪄", key=f"btn_{rid}"):
                            with st.spinner("מנתח..."):
                                raw = get_fathom_summary(rid)
                                if raw: st.session_state[s_key] = refine_with_ai(raw); st.rerun()
                    else: st.info(st.session_state[s_key])
        else: st.write("אין פגישות זמינות")
