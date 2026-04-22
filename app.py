import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
import google.generativeai as genai
from streamlit_js_eval import get_geolocation

# =========================================================
# 1. הגדרות דף ועיצוב (CSS המקורי והמלא)
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">', unsafe_allow_html=True)

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    .weather-float {
        position: absolute; top: 20px; left: 20px; z-index: 999;
        background: white; padding: 8px 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #edf2f7;
        text-align: center; display: flex; align-items: center; gap: 10px;
    }

    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important; font-size: 2.2rem !important;
        font-weight: 800; margin-bottom: 20px;
    }
    h3 { font-size: 1.15rem !important; font-weight: 700 !important; color: #1f2a44 !important; text-align: right !important; }
    
    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; border: 4px solid white !important; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }
    
    .kpi-card {
        background: white !important; padding: 15px !important; border-radius: 12px !important;
        text-align: center !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important; border-radius: 18px !important;
        padding: 15px !important; padding-bottom: 30px !important; 
    }

    .record-row {
        background: #ffffff !important; padding: 10px 15px !important;
        border-radius: 10px !important; margin-bottom: 3px !important;
        border: 1px solid #edf2f7 !important; border-right: 5px solid #4facfe !important;
        display: flex !important; justify-content: space-between !important;
        align-items: center !important; direction: rtl !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. לוגיקה: מזג אוויר ומיקום
# =========================================================

def get_weather(lat, lon):
    api_key = st.secrets["OPENWEATHER_API_KEY"]
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        data = requests.get(url).json()
        if data and data.get('main'):
            temp = round(data['main']['temp'])
            city_raw = data.get('name', '')
            # תרגום ידני למקרה שה-API מחזיר אנגלית
            trans = {"Petah Tikva": "פתח תקווה", "Petah Tiqwa": "פתח תקווה", "Tel Aviv": "תל אביב", "Holon": "חולון"}
            city = trans.get(city_raw, city_raw)
            icon_code = data['weather'][0]['icon']
            is_night = "n" in icon_code
            return {"temp": temp, "city": city, "is_night": is_night}
    except: return None

# הפעלת בקשת מיקום מהדפדפן
loc = get_geolocation()

# =========================================================
# 3. פונקציות עזר (אז'ור, פאטום וכו' - חזרה למקור)
# =========================================================

def get_azure_tasks():
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post("https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", 
                            json={"query": "SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New'"}, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/amandigital/_apis/wit/workitems?ids={ids}&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

# פונקציות פאטום המקוריות
def get_fathom_meetings():
    headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers=headers, timeout=10)
        return res.json().get('items', [])[:5], res.status_code
    except: return [], 500

# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except: st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df

# =========================================================
# 4. בניית הממשק (חזרה למבנה המקורי)
# =========================================================

# הצגת מזג אוויר אם המיקום אושר
if loc:
    w = get_weather(loc['coords']['latitude'], loc['coords']['longitude'])
    if w:
        icon = "bi-moon-stars-fill" if w['is_night'] else "bi-sun-fill"
        color = "#94a3b8" if w['is_night'] else "#FFD700"
        st.markdown(f"""
            <div class="weather-float">
                <div style="text-align:right">
                    <div style="font-size:0.7rem; color:#4facfe; font-weight:700;">{w['city']}</div>
                    <div style="font-size:1.1rem; color:#1f2a44; font-weight:800;">{w['temp']}°C</div>
                </div>
                <i class="bi {icon}" style="font-size:1.4rem; color:{color}"></i>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

# פרופיל
img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
with p3: st.markdown(f"<div><h3 style='margin-bottom:0;'>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# KPI
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

col_right, col_left = st.columns([1, 1])

with col_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים")
        for _, row in projects.iterrows():
            st.markdown(f'<div class="record-row"><b>📂 {row["project_name"]}</b><span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<h3>📋 משימות חדשות באז\'ור</h3>', unsafe_allow_html=True)
        tasks = get_azure_tasks()
        if tasks:
            for t in tasks:
                st.markdown(f'<div class="record-row"><span>🔗 {t["fields"]["System.Title"][:40]}</span><span class="tag-orange">Azure</span></div>', unsafe_allow_html=True)
        else: st.write("אין משימות")

with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        for _, r in t_m.iterrows():
            st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">היום</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        for _, row in t_r.iterrows():
            st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">דחוף</span></div>', unsafe_allow_html=True)

    # אזור פאטום - אחד לאחד
    with st.container(border=True):
        st.markdown("### ✨ סיכומי פגישות Fathom")
        if 'fathom_meetings' not in st.session_state:
            items, _ = get_fathom_meetings()
            st.session_state['fathom_meetings'] = items
        
        for idx, mtg in enumerate(st.session_state.get('fathom_meetings', [])):
            rec_id = mtg.get('recording_id')
            is_open = st.session_state.get(f"open_{rec_id}", False)
            st.markdown(f'<div class="record-row"><span>📅 {mtg.get("title", "פגישה")}</span><span class="material-symbols-rounded">{"expand_more" if is_open else "chevron_left"}</span></div>', unsafe_allow_html=True)
            if st.button("פתח/סגור", key=f"f_{rec_id}", use_container_width=True):
                st.session_state[f"open_{rec_id}"] = not is_open
                st.rerun()
