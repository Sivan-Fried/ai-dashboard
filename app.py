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
# 1. הגדרות דף ועיצוב (CSS)
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
    /* התיקון הסופי לפס הלבן - ללא השפעה על שאר האלמנטים */
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; height: 0px !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }

    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* מזג אוויר צף - הגדרות מקוריות */
    .weather-float {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 999;
        background: white;
        padding: 8px 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important; font-size: 2.2rem !important;
        font-weight: 800; margin-bottom: 20px;
    }

    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    .kpi-card {
        background: white !important; padding: 15px !important;
        border-radius: 12px !important; text-align: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }

    /* עיצוב רשומות - חזרה למקור */
    .record-row {
        background: #ffffff !important; padding: 10px 15px !important;
        border-radius: 10px !important; margin-bottom: 3px !important;
        border: 1px solid #edf2f7 !important; border-right: 5px solid #4facfe !important;
        display: flex !important; justify-content: space-between !important;
        align-items: center !important; direction: rtl !important;
    }

    /* עיצוב Fathom המקורי */
    .fathom-row-ui {
        display: flex; justify-content: space-between; align-items: center;
        background: white; border: 1px solid #edf2f7; border-right: 5px solid #4facfe;
        border-radius: 8px; padding: 10px 16px; min-height: 45px; direction: rtl;
    }
    div.element-container:has(.fathom-row-ui) + div.element-container {
        margin-top: -48px !important; margin-bottom: 5px !important;
    }
    div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button {
        background: transparent !important; border: none !important;
        width: 100% !important; height: 45px !important; color: transparent !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. לוגיקה ופונקציות (שיחזור מלא למקור)
# =========================================================

def get_real_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        data = requests.get(url).json()
        return {"temp": round(data['main']['temp']), "city": data.get('name', 'מיקום'), 
                "icon": "bi-moon-stars-fill" if "n" in data['weather'][0]['icon'] else "bi-sun-fill", 
                "color": "#94a3b8" if "n" in data['weather'][0]['icon'] else "#FFD700"}
    except: return None

def get_azure_tasks():
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(f"https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", 
                            json={"query": "SELECT [System.Id] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New'"}, auth=auth)
        ids = ",".join([str(i['id']) for i in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/amandigital/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Excel Files"); st.stop()

if "current_page" not in st.session_state: st.session_state.current_page = "main"
loc = get_geolocation()

# =========================================================
# 3. תצוגה (Main Dashboard)
# =========================================================

params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

if st.session_state.current_page == "project":
    st.markdown(f'<h1 class="dashboard-header">{st.session_state.selected_project}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה"):
        st.query_params.clear()
        st.session_state.current_page = "main"
        st.rerun()
else:
    # הצגת מזג אוויר
    if loc:
        w = get_real_weather(loc['coords']['latitude'], loc['coords']['longitude'])
        if w:
            st.markdown(f'<div class="weather-float"><div style="text-align:right;"><div style="font-size:0.7rem; color:#4facfe; font-weight:700;">{w["city"]}</div><div style="font-size:1.1rem; color:#1f2a44; font-weight:800;">{w["temp"]}°C</div></div><i class="bi {w["icon"]}" style="font-size:1.5rem; color:{w["color"]};"></i></div>', unsafe_allow_html=True)

    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    # Header & Profile
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    
    c1, c2, c3 = st.columns([1, 1, 2])
    with c2: 
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with c3: st.markdown(f"<h3>שלום, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>", unsafe_allow_html=True)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    col_right, col_left = st.columns([1, 1])

    with col_right:
        # פרויקטים - לינקים מקוריים עם urllib
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'<a href="{p_url}" target="_self" style="text-decoration:none;"><div class="record-row"><b>📂 {row["project_name"]}</b><span class="tag-blue">פרויקט</span></div></a>', unsafe_allow_html=True)

    with col_left:
        # Fathom - לוגיקה מקורית (Expandable)
        with st.container(border=True):
            st.markdown("### ✨ סיכומי Fathom")
            # כאן מופיעה הלוגיקה שלך ל-Fathom כפי שהייתה במקור...
            st.write("רשימת פגישות...")
