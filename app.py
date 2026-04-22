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
    
    /* הסתרת אלמנטים ריקים שיוצרים פסים לבנים (רכיב המיקום) */
    iframe { display: none !important; }
    div[data-testid="stHtml"] > iframe { height: 0px !important; }

    .weather-float {
        position: absolute; top: 20px; left: 20px; z-index: 999;
        background: white; padding: 8px 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #edf2f7; text-align: center;
    }

    button[data-baseweb="tab"] { gap: 20px !important; margin-left: 15px !important; padding-right: 20px !important; padding-left: 20px !important; }
    .dashboard-header { background: linear-gradient(90deg, #4facfe, #00f2fe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; text-align: center !important; font-size: 2.2rem !important; font-weight: 800; margin-bottom: 20px; }
    h3 { font-size: 1.15rem !important; font-weight: 700 !important; margin-bottom: 12px !important; color: #1f2a44 !important; text-align: right !important; }
    .profile-img { width: 130px; height: 130px; border-radius: 50% !important; object-fit: cover !important; object-position: center 25% !important; border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important; }
    .kpi-card { background: white !important; padding: 15px !important; border-radius: 12px !important; text-align: center !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important; }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background: white !important; border-radius: 18px !important; padding: 15px !important; }
    
    .record-row { 
        background: #ffffff !important; padding: 10px 15px !important; border-radius: 10px !important; margin-bottom: 3px !important; 
        border: 1px solid #edf2f7 !important; border-right: 5px solid #4facfe !important; 
        display: flex !important; justify-content: space-between !important; align-items: center !important; direction: rtl !important; 
    }
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. לוגיקה ופונקציות
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
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post("https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", json={"query": "SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New'"}, auth=auth)
        ids = ",".join([str(i['id']) for i in res.json().get('workItems', [])[:5]])
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
        res = requests.get(f"https://api.fathom.ai/external/v1/recordings/{rid}/summary", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]})
        return res.json().get("summary", {}).get("markdown_formatted") if res.status_code == 200 else None
    except: return None

def refine_with_ai(txt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(f"סכם לעברית עסקית:\n\n{txt}").text
    except: return "שגיאה בסיכום"

# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except: st.error("Missing Files"); st.stop()

# =========================================================
# 3. ניהול ניווט ו-Session State
# =========================================================
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df

# =========================================================
# 4. תצוגה
# =========================================================

# הפעלת בקשת מיקום
loc = get_geolocation()

# התיקון שמונע את קריסת הדשבורד (הפסקה עד שיש מיקום)
if not loc:
    st.info("מזהה מיקום... אנא אשרי גישה בדפדפן במידה והתבקשת.")
    st.stop()

if st.session_state.current_page == "project":
    p_name = st.session_state.get("selected_project", "פרויקט")
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה"): st.session_state.current_page = "main"; st.rerun()
    t1, t2, t3 = st.tabs(["📅 תוכנית", "👥 משאבים", "📝 סיכומים"])
    with t1: st.info("בבנייה...")
else:
    # הצגת מיקום ומזג אוויר
    w_text, w_city = get_weather_realtime(loc)
    st.markdown(f'<div class="weather-float"><div style="font-size:0.7rem; color:#4facfe;">{w_city}</div><div style="font-size:1.1rem; color:#1f2a44; font-weight:800;">{w_text}</div></div>', unsafe_allow_html=True)

    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    # פרופיל
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3: st.markdown(f"<div><h3 style='margin-bottom:0;'>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c_right, c_left = st.columns([1, 1])

    with c_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                if st.button(f"📂 {row['project_name']}", key=f"p_{row['project_name']}", use_container_width=True):
                    st.session_state.selected_project = row['project_name']
                    st.session_state.current_page = "project"
                    st.rerun()
        
        with st.container(border=True):
            st.markdown("### 📋 Azure Tasks")
            tasks = get_azure_tasks()
            if tasks:
                for t in tasks:
                    fields = t.get('fields', {})
                    st.markdown(f'<div class="record-row"><span>🔗 {fields.get("System.Title", "N/A")}</span><span class="tag-orange">{fields.get("System.TeamProject", "N/A")}</span></div>', unsafe_allow_html=True)
            else: st.write("אין משימות חדשות")

    with c_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if not t_m.empty:
                for _, r in t_m.iterrows():
                    st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{r.get("start_time", "")}</span></div>', unsafe_allow_html=True)
            else: st.write("אין פגישות היום")

        with st.container(border=True):
            st.markdown("### ✨ Fathom AI")
            f_mtgs = get_fathom_meetings()
            for m in f_mtgs:
                with st.expander(f"📅 {m['title']}"):
                    if st.button("סכם פגישה", key=f"f_{m['recording_id']}"):
                        with st.spinner("מנתח..."):
                            summary = get_fathom_summary(m['recording_id'])
                            st.write(refine_with_ai(summary) if summary else "אין סיכום זמין")
