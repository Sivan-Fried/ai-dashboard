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
st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">', unsafe_allow_html=True)

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

st.markdown("""
<style>
    /* הפתרון לפס הלבן - איפוס הדר ופאדינג עליון בלבד */
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; height: 0px !important; }
    .block-container { padding-top: 0rem !important; }

    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
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
    
    div[data-testid="stVerticalBlockBorderWrapper"], .st-emotion-cache-1ne20ew {
        background: white !important;
        border: 1.5px solid transparent !important;
        border-radius: 18px !important;
        padding: 15px !important;
        padding-bottom: 30px !important; 
    }

    .project-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block !important;
        transition: all 0.2s ease;
    }
    
    .project-link:hover .record-row {
        border-color: #4facfe !important;
        background-color: #f8fafc !important;
        transform: translateY(-1px);
        z-index: 5;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.15) !important;
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
        position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }

    .fathom-row-ui {
        display: grid;
        grid-template-columns: auto 1fr auto;
        align-items: center;
        background: white;
        border: 1px solid #edf2f7;
        border-right: 5px solid #4facfe;
        border-radius: 8px;
        padding: 0 16px;
        height: 45px;
        direction: rtl;
        transition: all 0.2s ease;
    }
    div[data-testid="stVerticalBlock"] > div:has(.fathom-row-ui) { gap: 0rem !important; }
    div.element-container:has(.fathom-row-ui) + div.element-container {
        margin-top: -45px !important;
        margin-bottom: 2px !important;
    }
    div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button {
        background: transparent !important;
        border: 1px solid transparent !important;
        width: 100% !important;
        height: 45px !important;
        color: transparent !important;
        z-index: 20;
    }
    .fathom-pill-v2 {
        background-color: #f1f5f9;
        color: #475569;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        margin-right: 12px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות נתונים
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
    wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject], [System.CreatedDate] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
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
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get("https://api.fathom.ai/external/v1/meetings", headers=headers, timeout=15)
        if response.status_code == 200: return response.json().get('items', [])[:5], 200
        return response.text, response.status_code
    except Exception as e: return str(e), 500

def get_fathom_summary(recording_id):
    api_key = st.secrets["FATHOM_API_KEY"]
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary", headers=headers, timeout=15)
        if response.status_code == 200: return response.json().get("summary", {}).get("markdown_formatted")
        return None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"סכם את הפגישה לעברית עסקית רהוטה. מבנה: נושא, תקציר מנהלים, החלטות מרכזיות ומשימות:\n\n{raw_text}"
        return model.generate_content(prompt).text
    except Exception as e: return f"שגיאה: {e}"

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

# ניהול State
loc = get_geolocation()
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "current_page" not in st.session_state: st.session_state.current_page = "main"

params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

# =========================================================
# 3. תצוגה
# =========================================================

if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear() 
        st.session_state.current_page = "main"
        st.rerun()
    
    with st.container(border=True):
        st.markdown(f"### ℹ️ ניהול פרויקט: {p_name}")
        tab_work, tab_res, tab_risk, tab_meetings, tab_info = st.tabs(["📅 תוכנית עבודה", "👥 משאבים", "⚠️ סיכונים", "📝 סיכומי פגישות", "📊 מידע כללי"])
        with tab_work: st.info(f"תוכנית עבודה עבור {p_name} תעודכן בהמשך.")
        with tab_res: st.write("משאבים")
        with tab_risk: st.write("סיכונים")
        with tab_meetings: st.write("סיכומים")
        with tab_info: st.write("מידע")

else:
    if loc:
        w_data = get_real_weather(loc['coords']['latitude'], loc['coords']['longitude'])
        if w_data:
            st.markdown(f"""
                <div class="weather-float">
                    <div style="text-align: right;">
                        <div style="font-size: 0.7rem; color: #4facfe; font-weight: 700;">{w_data['city']}</div>
                        <div style="font-size: 1.1rem; color: #1f2a44; font-weight: 800;">{w_data['temp']}°C</div>
                    </div>
                    <i class="bi {w_data['icon']}" style="font-size: 1.5rem; color: {w_data['color']};"></i>
                </div>
            """, unsafe_allow_html=True)

    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3: st.markdown(f"<div><h3 style='margin-bottom:0;'>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([1, 1])

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            with st.container(height=300, border=False):
                for _, row in projects.iterrows():
                    p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                    st.markdown(f'''<a href="{p_url}" target="_self" class="project-link"><div class="record-row"><div style="display:flex;align-items:center;gap:10px;"><b>📂 {row["project_name"]}</b><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div><span class="material-symbols-rounded" style="color:#94a3b8;font-size:20px;">chevron_left</span></div></a>''', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<h3>📋 משימות Azure</h3>', unsafe_allow_html=True)
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {}); t_title = f.get('System.Title', ''); p_task = f.get('System.TeamProject', 'General')
                    st.markdown(f'<div class="record-row"><div style="flex-grow:1;text-align:right;">🔗 {t_title}</div><span class="tag-orange">{p_task}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            a1, a2 = st.columns([1, 2]); sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), key="ai_p", label_visibility="collapsed")
            q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", key="ai_i", label_visibility="collapsed")
            if st.button("שאל 🚀", use_container_width=True):
                st.session_state.ai_response = f"**ניתוח עבור {sel_p}:** תקין."
            if st.session_state.ai_response: st.info(st.session_state.ai_response)

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty: st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    st.markdown(f'<div class="record-row"><span style="flex-grow:1;text-align:right;">📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r.get("start_time"))}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)
#fathom
        # --- אזור Fathom המעודכן ---
        with st.container(border=True):
            col_title, col_refresh = st.columns([0.9, 0.1])
            with col_title:
                st.markdown("### ✨ סיכומי פגישות Fathom")

            with col_refresh:
                if st.button("🔄", key="refresh_fathom"):
                    try:
                        items, status = get_fathom_meetings()
                        if status == 200:
                            st.session_state['fathom_meetings'] = items
                            st.rerun()
                    except: pass

            if 'fathom_meetings' not in st.session_state:
                try:
                    items, status = get_fathom_meetings()
                    if status == 200:
                        st.session_state['fathom_meetings'] = items
                    else:
                        st.session_state['fathom_meetings'] = []
                except:
                    st.session_state['fathom_meetings'] = []

            st.markdown("""
                <style>
                .fathom-row-ui {
                    display: grid;
                    grid-template-columns: auto 1fr auto;
                    align-items: center;
                    background: white;
                    border: 1px solid #edf2f7;
                    border-right: 5px solid #4facfe;
                    border-radius: 8px;
                    padding: 0 16px;
                    height: 45px;
                    direction: rtl;
                    transition: all 0.2s ease;
                }
                div[data-testid="stVerticalBlock"] > div:has(.fathom-row-ui) {
                    gap: 0rem !important;
                }
                div.element-container:has(.fathom-row-ui) + div.element-container {
                    margin-top: -45px !important;
                    margin-bottom: 2px !important;
                }
                div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button {
                    background: transparent !important;
                    border: 1px solid transparent !important;
                    border-right: 5px solid transparent !important;
                    width: 100% !important;
                    height: 45px !important;
                    color: transparent !important;
                    z-index: 20;
                }
                div.element-container:has(.fathom-row-ui):has(+ div.element-container div[data-testid="stButton"] button:hover) .fathom-row-ui {
                    border-color: #4facfe;
                    background-color: #f8fafc;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }
                .fathom-pill-v2 {
                    background-color: #f1f5f9;
                    color: #475569;
                    padding: 1px 8px;
                    border-radius: 10px;
                    font-size: 0.75rem;
                    margin-right: 12px;
                }
                </style>
            """, unsafe_allow_html=True)

            f_meetings = st.session_state.get('fathom_meetings', [])

            if f_meetings:
                for idx, mtg in enumerate(f_meetings):
                    rec_id = mtg.get('recording_id')
                    title = mtg.get('title') or "פגישה"
                    date_str = mtg.get('recording_start_time', '')[:10]

                    open_key = f"open_{rec_id}"
                    is_open = st.session_state.get(open_key, False)
                    arrow = "expand_more" if is_open else "chevron_left"

                    st.markdown(f'''
                        <div class="fathom-row-ui">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.1rem; margin-left: 10px;">📅</span>
                                <span style="font-weight: 600; color: #1e293b; font-size: 0.85rem;">{title}</span>
                                <span class="fathom-pill-v2">{date_str}</span>
                            </div>
                            <div></div>
                            <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">{arrow}</span>
                        </div>
                    ''', unsafe_allow_html=True)

                    if st.button("", key=f"f_trig_{rec_id}_{idx}", use_container_width=True):
                        st.session_state[open_key] = not is_open
                        st.rerun()

                    if is_open:
                        with st.container():
                            s_key = f"sum_v4_{rec_id}"
                            if s_key not in st.session_state:
                                if st.button("צור סיכום עם AI 🪄", key=f"gen_{rec_id}"):
                                    with st.spinner("מנתח..."):
                                        raw = get_fathom_summary(rec_id)
                                        if raw:
                                            st.session_state[s_key] = refine_with_ai(raw)
                                            st.rerun()
                            else:
                                st.info(st.session_state[s_key])
            else:
                st.write("אין פגישות זמינות.")
