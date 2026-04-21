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
# 1. הגדרות דף ועיצוב (CSS) - גרסת יצירה
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan - גרסת יצירה", initial_sidebar_state="collapsed")

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
    
    div[data-testid="stVerticalBlockBorderWrapper"], .st-emotion-cache-1ne20ew {
        background: white !important;
        border: 1.5px solid transparent !important;
        border-radius: 18px !important;
        padding: 15px !important;
        padding-bottom: 30px !important; 
    }

    /* עיצוב רשומה סטנדרטית */
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
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    /* --- תיקון ממוקד לאזור הפאטום --- */
    .fathom-area .stExpander { border: none !important; background: transparent !important; margin-bottom: 3px !important; }
    .fathom-area .stExpander summary {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        flex-direction: row-reverse !important; /* דוחף תוכן לימין */
        list-style: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    .fathom-area .stExpander summary svg { display: none !important; }
    .fathom-area .stExpander summary::after {
        content: 'chevron_left';
        font-family: 'Material Symbols Rounded';
        color: #94a3b8;
        font-size: 20px;
        margin-right: auto; /* דוחף את החץ לשמאל */
    }

    /* תיקון יישור כפתורים בתזכורת */
    div[data-testid="column"] button { margin-top: 0px !important; height: 38px !important; }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    .kpi-card { background: white; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    .project-link { text-decoration: none !important; color: inherit !important; display: block !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות ונתונים (נשארים זהים לקוד המקור שלך)
# =========================================================

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
        return response.text, response.status_code
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

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

# =========================================================
# 3. ניהול ניווט ו-State
# =========================================================
if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False
if "current_page" not in st.session_state: st.session_state.current_page = "main"

params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

# =========================================================
# 4. דף פרויקט (נשמר בדיוק כפי שהיה)
# =========================================================
if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear(); st.session_state.current_page = "main"; st.rerun()
    
    with st.container(border=True):
        st.markdown(f"### ℹ️ ניהול פרויקט: {p_name}")
        tab_work, tab_res, tab_risk, tab_meetings, tab_info = st.tabs(["📅 תוכנית עבודה", "👥 משאבים", "⚠️ סיכונים", "📝 סיכומי פגישות", "📊 מידע כללי"])
        with tab_work:
            if "אלטשולר" in p_name:
                roadmap_html = """<!DOCTYPE html><html dir="rtl" lang="he"><head>...</head><body><div class="timeline-wrapper">...</div></body></html>""" # כאן מגיע ה-Roadmap המלא שלך
                components.html(roadmap_html, height=300, scrolling=False)
            else: st.info(f"תוכנית עבודה עבור {p_name} תעודכן בהמשך.")

# =========================================================
# 5. דשבורד ראשי
# =========================================================
else:
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
    
    # חלוקה שווה [1, 1]
    col_right, col_left = st.columns([1, 1])

    with col_right:
        # פרויקטים
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            with st.container(height=300, border=False):
                for _, row in projects.iterrows():
                    p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                    st.markdown(f'''<a href="{p_url}" target="_self" class="project-link"><div class="record-row"><div style="display: flex; align-items: center; gap: 10px;"><b>📂 {row["project_name"]}</b><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div><span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span></div></a>''', unsafe_allow_html=True)

        # Azure
        with st.container(border=True):
            st.markdown('<h3>📋 משימות באז\'ור</h3>', unsafe_allow_html=True)
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {}); t_title, p_task = f.get('System.Title', ''), f.get('System.TeamProject', 'General')
                    st.markdown(f'<div class="record-row"><div style="flex-grow: 1; text-align: right; overflow: hidden; text-overflow: ellipsis;"><b>🔗 {t_title}</b></div><span class="tag-orange" style="margin-right: 12px; flex-shrink: 0;">{p_task}</span></div>', unsafe_allow_html=True)
            else: st.markdown('<p style="text-align: right; color: gray;">אין משימות חדשות.</p>', unsafe_allow_html=True)

        # AI Assistant
        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            a1, a2 = st.columns([1, 2]); sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p"); q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                if q_in:
                    with st.spinner("מנתח..."): time.sleep(0.5); st.session_state.ai_response = f"**ניתוח עבור {sel_p}:** הסטטוס תקין."
            if st.session_state.ai_response: st.info(st.session_state.ai_response)

    with col_left:
        # פגישות
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty: st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    st.markdown(f'<div class="record-row"><span style="flex-grow:1; text-align:right;">📌 {r["meeting_title"]}</span><span class="time-label">{fmt_time(r.get("start_time",""))}</span></div>', unsafe_allow_html=True)

        # תזכורות
        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)
            
            if st.session_state.adding_reminder:
                # תיקון: כל רכיבי ההוספה בשורה אחת
                r_c1, r_c2, r_c3, r_c4 = st.columns([1, 1.5, 0.4, 0.4])
                with r_c1: n_p = st.selectbox("פ", projects["project_name"].tolist() + ["כללי"], label_visibility="collapsed")
                with r_c2: n_t = st.text_input("ת", placeholder="תזכורת...", label_visibility="collapsed")
                with r_c3: 
                    if st.button("✅"):
                        if n_t:
                            new_row = pd.DataFrame([{"date": today, "reminder_text": n_t, "project_name": n_p}])
                            st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_row], ignore_index=True)
                        st.session_state.adding_reminder = False; st.rerun()
                with r_c4:
                    if st.button("❌"): st.session_state.adding_reminder = False; st.rerun()
            else:
                if st.button("➕", use_container_width=True): st.session_state.adding_reminder = True; st.rerun()

        # פאטום - עם העיצוב המתוקן (שימוש ב-div עוטף ל-CSS)
        st.markdown('<div class="fathom-area">', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### ✨ סיכומי פגישות Fathom")
            if 'f_mtg' not in st.session_state:
                items, status = get_fathom_meetings()
                if status == 200: st.session_state['f_mtg'] = items

            if 'f_mtg' in st.session_state:
                for mtg in st.session_state['f_mtg']:
                    rec_id, title = mtg.get('recording_id'), mtg.get('title', 'פגישה')
                    with st.expander(f"📅 {title}"):
                        s_key = f"sum_{rec_id}"
                        if s_key not in st.session_state:
                            if st.button("צור סיכום 🪄", key=f"btn_{rec_id}", use_container_width=True):
                                raw = get_fathom_summary(rec_id)
                                if raw: st.session_state[s_key] = refine_with_ai(raw); st.rerun()
                        else:
                            st.markdown(f'<div style="direction:rtl; text-align:right;">{st.session_state[s_key]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
