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
    
    button[data-baseweb="tab"] {
        gap: 20px !important;
        margin-left: 15px !important;
        padding-right: 20px !important;
        padding-left: 20px !important;
    }

    /* ← תיקון הפס הלבן של get_geolocation */
    iframe[title="streamlit_js_eval.streamlit_js_eval"] {
        display: none !important;
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

    .project-link:first-child .record-row, .record-row:first-of-type {
        margin-top: 4px !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }

    /* Weather inline */
    .weather-float {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        background: white;
        padding: 8px 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
    }
    div[data-testid="stMarkdownContainer"]:has(.weather-float) {
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות עזר ונתונים
# =========================================================

def get_weather_realtime(location):
    if location and 'coords' in location:
        lat, lon = location['coords']['latitude'], location['coords']['longitude']
        try:
            # זיהוי עיר
            g = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}", headers={'User-Agent': 'SivanDash'}).json()
            city = g.get('address', {}).get('city') or g.get('address', {}).get('town') or "ישראל"
            
            # נתוני מזג אוויר
            w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
            temp = round(w['current_weather']['temperature'])
            
            # בדיקה האם עכשיו יום או לילה לפי השעה המקומית
            hour = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).hour
            icon = "🌙" if (hour >= 19 or hour < 6) else "☀️"
            
            return f"{icon} {temp}°C", city
        except: pass
    return "☀️ --°C", "ישראל"

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
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200: return response.json().get("summary", {}).get("markdown_formatted")
        return None
    except: return None

# החלף את הפונקציה refine_with_ai
def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        prompt = f"סכם את הפגישה לעברית עסקית רהוטה:\n\n{raw_text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה בסיכום: {str(e)}"

def fmt_time(t):
    try: return t.strftime("%H:%M")
    except: return ""

# פונקציה לשמירת סיכומים שנוצרים לתוך אקסל
def save_summary_to_excel(title, date_str, summary_text):
    file_path = "fathom_summaries.xlsx"
    new_row = {
        "title": title,
        "date": date_str,
        "summary": summary_text,
        "created_at": datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d/%m/%Y %H:%M")
    }
    try:
        existing = pd.read_excel(file_path)
        if "title" not in existing.columns:
            updated = pd.DataFrame([new_row])
        elif title in existing["title"].values:
            return
        else:
            updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
    except FileNotFoundError:
        updated = pd.DataFrame([new_row])
    updated.to_excel(file_path, index=False)
    
# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files (my_projects, meetings, reminders)"); st.stop()

# =========================================================
# 3. ניהול ניווט ו-Session State
# =========================================================
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False

params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

# =========================================================
# 4. מבנה התצוגה
# =========================================================

# קבלת מיקום
loc = get_geolocation()

if st.session_state.current_page == "project":
    # --- דף פרויקט ספציפי ---
    p_name = st.session_state.get("selected_project", "פרויקט")
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear()
        st.session_state.current_page = "main"
        st.rerun()
    
    with st.container(border=True):
        st.markdown(f"### ℹ️ ניהול פרויקט: {p_name}")
        tab_work, tab_res, tab_risk, tab_meetings = st.tabs(["📅 תוכנית עבודה", "👥 משאבים", "⚠️ סיכונים", "📝 סיכומים"])
        with tab_work:
            if p_name == "אלטשולר שחם":
                exec(open("altshuler_module.py").read())
            else:
                st.info(f"תוכנית עבודה עבור {p_name} בטעינה...")
        with tab_res: st.write("רשימת צוות ומשאבים")
        with tab_risk: st.write("ניהול סיכונים")
        with tab_meetings: st.write("סיכומי פגישות הפרויקט")

else:
    # --- דף ראשי (דשבורד) ---
    
    # מזג אוויר צף
    if loc:
        w_text, w_city = get_weather_realtime(loc)
    else:
        w_text, w_city = "☀️ --°C", "מזהה מיקום..."
        
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

    # אזור פרופיל
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64:
            st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3:
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 style='margin-bottom:0;'>{greeting}, סיון!</h3>
                    <p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>
                </div>
                <div class="weather-float">
                    <div style="font-size: 0.7rem; color: #4facfe; font-weight: 700;">{w_city}</div>
                    <div style="font-size: 1.1rem; color: #1f2a44; font-weight: 800;">{w_text}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPIs
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
                    st.markdown(f'''
                        <a href="{p_url}" target="_self" class="project-link">
                            <div class="record-row">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <b>📂 {row["project_name"]}</b>
                                    <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                                </div>
                                <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span>
                            </div>
                        </a>
                    ''', unsafe_allow_html=True)
                    
        with st.container(border=True):
            st.markdown('<h3>📋 משימות חדשות באז\'ור</h3>', unsafe_allow_html=True)
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {}); t_id, t_title, p_task = t.get('id'), f.get('System.Title', ''), f.get('System.TeamProject', 'General')
                    raw_date = f.get('System.CreatedDate', ''); fmt_date = f"{raw_date[8:10]}/{raw_date[5:7]} {raw_date[11:16]}" if raw_date else ""
                    t_url = f"https://dev.azure.com/amandigital/{urllib.parse.quote(p_task)}/_workitems/edit/{t_id}"
                    st.markdown(f'<div class="record-row" style="white-space: nowrap;"><div style="flex-grow: 1; text-align: right; overflow: hidden; text-overflow: ellipsis;"><a href="{t_url}" target="_blank" style="color: #0078d4; text-decoration: none; font-weight: 500;">🔗 {t_title}</a><span style="color: #94a3b8; font-size: 0.8rem; margin-right: 15px;">נוצר ב {fmt_date}</span></div><span class="tag-orange" style="margin-right: 12px; flex-shrink: 0;">{p_task}</span></div>', unsafe_allow_html=True)
            else: st.markdown('<p style="text-align: right; color: gray;">אין משימות חדשות.</p>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            a1, a2 = st.columns([1, 2])
            sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
            q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
            
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                    if q_in:
                        with st.spinner("מנתח..."):
                            try:
                                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                                proj_row = projects[projects["project_name"] == sel_p].iloc[0]
                                prompt = f"""אתה עוזר AI לניהול פרויקטים.
            פרויקט: {sel_p}
            סטטוס: {proj_row.get('status', 'לא ידוע')}
            שאלה: {q_in}
            ענה בעברית עסקית, קצר וממוקד."""
                                response = model.generate_content(prompt)
                                st.session_state.ai_response = response.text
                            except Exception as e:
                                st.session_state.ai_response = f"שגיאה: {str(e)}"
        
        if st.session_state.ai_response:
            st.info(st.session_state.ai_response)
            
    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty: st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    s_t = fmt_time(r.get('start_time', '')); e_t = fmt_time(r.get('end_time', ''))
                    st.markdown(f'<div class="record-row"><span style="flex-grow:1; text-align:right;">📌 {r["meeting_title"]}</span><span class="time-label">{s_t}-{e_t}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            with st.container(border=False):
                t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
                if not t_r.empty:
                    for _, row in t_r.iterrows():
                        st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)
                else: st.write("אין תזכורות להיום.")
            
            if st.session_state.adding_reminder:
                with st.container():
                    r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 3, 0.5, 0.5])
                    with r_col1: new_proj = st.selectbox("פרויקט", projects["project_name"].tolist() + ["כללי"], label_visibility="collapsed", key="new_rem_proj")
                    with r_col2: new_text = st.text_input("תיאור", placeholder="מה להזכיר?", label_visibility="collapsed", key="new_rem_text")
                    with r_col3:
                        if st.button("✅", key="save_rem_btn"):
                            if new_text:
                                new_row = {"date": today, "reminder_text": new_text, "project_name": new_proj}
                                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([new_row])], ignore_index=True)
                                st.session_state.adding_reminder = False; st.rerun()
                    with r_col4:
                        if st.button("❌", key="cancel_rem_btn"): st.session_state.adding_reminder = False; st.rerun()
            else:
                if st.button("➕ הוספת תזכורת", use_container_width=True): st.session_state.adding_reminder = True; st.rerun()
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
                div[data-testid="stAlert"] { direction: rtl; text-align: right; }
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
                    s_key = f"sum_v4_{rec_id}"

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
                            if s_key not in st.session_state:
                                if st.button("צור סיכום עם AI 🪄", key=f"gen_{rec_id}"):
                                    with st.spinner("מנתח..."):
                                        raw = get_fathom_summary(rec_id)
                                        if raw:
                                            summary = refine_with_ai(raw)
                                            st.session_state[s_key] = summary
                                            save_summary_to_excel(title, date_str, summary)
                                        else:
                                            st.session_state[s_key] = "לא נמצא תוכן לסיכום"
                            
                            if st.session_state.get(s_key):
                                st.info(st.session_state.get(s_key))
            else:
                st.write("אין פגישות זמינות.")
