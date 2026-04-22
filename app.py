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

# טעינת פונטים ואייקונים
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">', unsafe_allow_html=True)

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

st.markdown("""
<style>
    /* הפתרון לפס הלבן - איפוס הדר ופאדינג */
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; height: 0px !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* מזג אוויר - נשמר בדיוק לפי העיצוב המקורי שלך */
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
        text-align: center;
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

    .record-row {
        background: #ffffff !important; padding: 10px 15px !important;
        border-radius: 10px !important; margin-bottom: 3px !important;
        border: 1px solid #edf2f7 !important; border-right: 5px solid #4facfe !important;
        display: flex !important; justify-content: space-between !important;
        align-items: center !important; direction: rtl !important;
    }

    /* עיצוב Fathom - החזרתי למקור */
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
# 2. פונקציות (ללא שינוי)
# =========================================================

def get_real_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        data = requests.get(url).json()
        temp = round(data['main']['temp'])
        city_en = data.get('name', '')
        translate = {"Petah Tikva": "פתח תקווה", "Holon": "חולון", "Tel Aviv": "תל אביב"}
        city_he = translate.get(city_en, city_en)
        icon_code = data['weather'][0]['icon']
        icon_class = "bi-moon-stars-fill" if "n" in icon_code else "bi-sun-fill"
        icon_color = "#94a3b8" if "n" in icon_code else "#FFD700"
        return {"temp": temp, "city": city_he, "icon": icon_class, "color": icon_color}
    except: return None

def get_azure_tasks():
    ORG_NAME = "amandigital"
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
        query = {"query": "SELECT [System.Id] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers=headers, timeout=10)
        return res.json().get('items', [])[:5] if res.status_code == 200 else []
    except: return []

def get_fathom_summary(recording_id):
    headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
    try:
        res = requests.get(f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary", headers=headers)
        return res.json().get("summary", {}).get("markdown_formatted") if res.status_code == 200 else None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"סכם לעברית עסקית:\n\n{raw_text}").text
    except: return "שגיאה בעיבוד ה-AI"

# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Excel files"); st.stop()

# ניהול State
if "current_page" not in st.session_state: st.session_state.current_page = "main"
loc = get_geolocation()

# =========================================================
# 3. ניווט ותצוגה
# =========================================================

# לוגיקה למעבר דפים (לפי הפרמטרים ב-URL)
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
    st.write("פרטי הפרויקט יוצגו כאן.")

else:
    # מזג אוויר (Floating)
    if loc:
        w = get_real_weather(loc['coords']['latitude'], loc['coords']['longitude'])
        if w:
            st.markdown(f'''
                <div class="weather-float">
                    <div style="text-align:right;">
                        <div style="font-size:0.7rem; color:#4facfe; font-weight:700;">{w["city"]}</div>
                        <div style="font-size:1.1rem; color:#1f2a44; font-weight:800;">{w["temp"]}°C</div>
                    </div>
                    <i class="bi {w["icon"]}" style="font-size:1.5rem; color:{w["color"]};"></i>
                </div>
            ''', unsafe_allow_html=True)

    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    # Header ופרופיל
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
    
    c1, c2, c3 = st.columns([1, 1, 2])
    with c2: 
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with c3: st.markdown(f"<h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>", unsafe_allow_html=True)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    col_right, col_left = st.columns([1, 1])

    with col_right:
        # פרויקטים (עם שימוש ב-urllib כפי שביקשת)
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'''<a href="{p_url}" target="_self" style="text-decoration:none;"><div class="record-row"><b>📂 {row["project_name"]}</b><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div></a>''', unsafe_allow_html=True)

        # משימות Azure
        with st.container(border=True):
            st.markdown("### 📋 משימות Azure")
            for t in get_azure_tasks():
                f = t.get('fields', {})
                st.markdown(f'<div class="record-row"><span>🔗 {f.get("System.Title", "")[:30]}</span><span class="tag-orange">{f.get("System.TeamProject", "")}</span></div>', unsafe_allow_html=True)

    with col_left:
        # סיכומי Fathom - לוגיקה מקורית
        with st.container(border=True):
            st.markdown("### ✨ סיכומי Fathom")
            f_mtgs = get_fathom_meetings()
            for idx, mtg in enumerate(f_mtgs):
                rec_id = mtg.get('recording_id')
                open_key = f"open_{rec_id}"
                st.markdown(f'''<div class="fathom-row-ui"><span>📅 {mtg.get("title")[:25]}</span><span class="material-symbols-rounded">chevron_left</span></div>''', unsafe_allow_html=True)
                if st.button("", key=f"btn_{rec_id}_{idx}", use_container_width=True):
                    st.session_state[open_key] = not st.session_state.get(open_key, False)
                    st.rerun()
                
                if st.session_state.get(open_key, False):
                    s_key = f"sum_{rec_id}"
                    if s_key not in st.session_state:
                        if st.button("צור סיכום ✨", key=f"g_{rec_id}"):
                            raw = get_fathom_summary(rec_id)
                            if raw: st.session_state[s_key] = refine_with_ai(raw)
                            st.rerun()
                    else: st.info(st.session_state[s_key])
