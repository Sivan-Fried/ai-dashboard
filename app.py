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
# 1. פונקציות עזר (בדיוק כפי שהיו)
# =========================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

def get_fathom_meetings():
    api_key = st.secrets["FATHOM_API_KEY"]
    url = "https://api.fathom.ai/external/v1/meetings"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('items', [])[:5], 200
        return response.text, response.status_code
    except Exception as e: return str(e), 500

def get_fathom_summary(recording_id):
    api_key = st.secrets["FATHOM_API_KEY"]
    url = f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("summary", {}).get("markdown_formatted")
        return None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro'] if m in available_models), available_models[0])
        model = genai.GenerativeModel(selected_model)
        prompt = f"סכם את הפגישה לעברית עסקית רהוטה. מבנה: נושא, תקציר מנהלים, החלטות מרכזיות ומשימות:\n\n{raw_text}"
        return model.generate_content(prompt).text
    except Exception as e: return f"שגיאה: {e}"

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

def fmt_time(t):
    try: return t.strftime("%H:%M")
    except: return ""

# =========================================================
# 2. טעינת נתונים ו-CSS (המקור שלך)
# =========================================================
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings_df = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

st.markdown("""
<style>
    .dashboard-header { text-align: right; color: #1e293b; font-weight: 800; margin-bottom: 20px; }
    .kpi-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border: 1px solid #f1f5f9; }
    .profile-img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #4facfe; }
    .record-row { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #f1f5f9; direction: rtl; }
    .project-link { text-decoration: none; color: inherit; }
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# State
params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False
if "current_page" not in st.session_state: st.session_state.current_page = "main"

# =========================================================
# 3. תצוגת דפים
# =========================================================

if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear() 
        st.session_state.current_page = "main"
        st.rerun()
    
    with st.container(border=True):
        tab_work, tab_res, tab_risk, tab_meetings, tab_info = st.tabs(["📅 תוכנית עבודה", "👥 משאבים", "⚠️ סיכונים", "📝 סיכומי פגישות", "📊 מידע כללי"])
        with tab_work:
            if "אלטשולר" in p_name:
                roadmap_html = """<html dir="rtl"><body style="margin:0;"><div style="width:1000px; height:200px; background:#f8fafc; border-radius:10px; display:flex; align-items:center; justify-content:center;">תרשים לוח זמנים אלטשולר</div></body></html>"""
                components.html(roadmap_html, height=300)
            else: st.info("תוכנית עבודה תעודכן בהמשך.")

else:
    # דשבורד ראשי
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
    col_right, col_left = st.columns([2, 1.2])

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'<a href="{p_url}" target="_self" class="project-link"><div class="record-row"><b>📂 {row["project_name"]}</b><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div></a>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<h3>📋 משימות חדשות באז\'ור</h3>', unsafe_allow_html=True)
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    t_title = t.get('fields', {}).get('System.Title', '')
                    st.markdown(f'<div class="record-row"><span>🔗 {t_title}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            q_in = st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed")
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                st.session_state.ai_response = "ניתוח בביצוע..."

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings_df[pd.to_datetime(meetings_df["date"]).dt.date == today]
            if t_m.empty: st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
            if st.button("➕", use_container_width=True):
                st.session_state.adding_reminder = True; st.rerun()

        # --- התיקון שביקשת: פאטום כאן, מתחת לתזכורות, טוען לבד ---
        with st.container(border=True):
            st.markdown("### ✨ סיכומי פגישות Fathom")
            if 'fathom_meetings' not in st.session_state:
                items, status = get_fathom_meetings()
                if status == 200: st.session_state['fathom_meetings'] = items

            if 'fathom_meetings' in st.session_state:
                for mtg in st.session_state['fathom_meetings']:
                    rec_id, title = mtg.get('recording_id'), mtg.get('title', 'פגישה')
                    s_key = f"sum_fixed_{rec_id}"
                    with st.expander(f"📅 {title}"):
                        if s_key not in st.session_state:
                            if st.button("צור סיכום 🪄", key=f"btn_{rec_id}", use_container_width=True):
                                raw = get_fathom_summary(rec_id)
                                if raw:
                                    st.session_state[s_key] = refine_with_ai(raw)
                                    st.rerun()
                        else:
                            st.markdown(f'<div style="direction:rtl; text-align:right; background:#f9f9f9; padding:15px; border-radius:10px; border:1px solid #eee;">{st.session_state[s_key]}</div>', unsafe_allow_html=True)
                            if st.button("נקה 🗑️", key=f"del_{rec_id}"):
                                del st.session_state[s_key]; st.rerun()
