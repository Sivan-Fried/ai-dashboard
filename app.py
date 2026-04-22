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
# 1. הגדרות דף ועיצוב (CSS) - המקור המדויק ללא הפס
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
    
    /* העלמת הפס האפור מתחת לטאבים */
    div[data-baseweb="tab-border"] { display: none !important; }
    div[data-baseweb="tab-list"] { border-bottom: none !important; }

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
    }

    button[data-baseweb="tab"] {
        gap: 20px !important;
        margin-left: 15px !important;
        padding-right: 20px !important;
        padding-left: 20px !important;
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
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, div { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות עזר ומיקום אמיתי
# =========================================================

def get_weather_by_coords(location):
    if location and 'coords' in location:
        lat, lon = location['coords']['latitude'], location['coords']['longitude']
        try:
            # משיכת שם העיר האמיתי
            geo = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}", headers={'User-Agent': 'SivanDash'}).json()
            city = geo.get('address', {}).get('city') or geo.get('address', {}).get('town') or "מיקום נוכחי"
            w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
            temp = round(w_res['current_weather']['temperature'])
            return f"☀️ {city}, {temp}°C"
        except: return "☀️ מזהה מיקום..."
    return "☀️ טוען מיקום..."

def get_azure_tasks():
    ORG_NAME = "amandigital"
    wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject,System.CreatedDate&api-version=6.0", auth=auth)
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
        res = requests.get(url, headers=headers, timeout=15)
        return res.json().get("summary", {}).get("markdown_formatted") if res.status_code == 200 else None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"סכם לעברית עסקית:\n\n{raw_text}"
        return model.generate_content(prompt).text
    except: return "שגיאה בסיכום"

def fmt_time(t):
    try: return t.strftime("%H:%M")
    except: return ""

# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

# =========================================================
# 3. ניווט ותצוגה
# =========================================================

if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""

# --- דף פרויקט ---
if st.session_state.get("selected_project") and st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה"):
        st.session_state.current_page = "main"
        st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["📅 תוכנית", "👥 משאבים", "📝 סיכומים"])
    with tab1: st.info("תוכנית עבודה בבנייה...")

# --- דף ראשי ---
else:
    # שליפת מיקום
    user_loc = get_geolocation()
    weather_info = get_weather_by_coords(user_loc)
    st.markdown(f'<div class="weather-float"><div style="font-size:0.7rem; color:#4facfe;">המיקום שלי</div><div style="font-size:1.1rem; color:#1f2a44; font-weight:800;">{weather_info}</div></div>', unsafe_allow_html=True)

    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    # פרופיל
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3: st.markdown(f"<div><h3 style='margin-bottom:0;'>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    # KPIs
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    col_right, col_left = st.columns([1, 1])

    with col_right:
        # פרויקטים
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                if st.button(f"📂 {row['project_name']}", key=f"p_{row['project_name']}", use_container_width=True):
                    st.session_state.selected_project = row['project_name']
                    st.session_state.current_page = "project"
                    st.rerun()

        # Azure
        with st.container(border=True):
            st.markdown("### 📋 Azure Tasks")
            tasks = get_azure_tasks()
            for t in tasks:
                st.markdown(f'<div class="record-row"><span>🔗 {t["fields"]["System.Title"]}</span><span class="tag-orange">{t["fields"]["System.TeamProject"]}</span></div>', unsafe_allow_html=True)

    with col_left:
        # פגישות
        with st.container(border=True):
            st.markdown("### 📅 היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r["start_time"])}</span></div>', unsafe_allow_html=True)

        # Fathom
        with st.container(border=True):
            st.markdown("### ✨ Fathom AI")
            f_meetings, _ = get_fathom_meetings()
            for mtg in f_meetings:
                with st.expander(f"📅 {mtg['title']}"):
                    if st.button("סכם פגישה", key=f"btn_{mtg['recording_id']}"):
                        raw = get_fathom_summary(mtg['recording_id'])
                        st.write(refine_with_ai(raw))
