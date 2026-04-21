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
# 1. פונקציות לוגיקה (המנוע של האפליקציה)
# =========================================================

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

@st.cache_data(ttl=3600)
def get_fathom_meetings_auto():
    api_key = st.secrets["FATHOM_API_KEY"]
    url = "https://api.fathom.ai/external/v1/meetings"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('items', [])[:5]
        return []
    except: return []

def get_fathom_summary_raw(recording_id):
    api_key = st.secrets["FATHOM_API_KEY"]
    url = f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("summary", {}).get("markdown_formatted")
        return None
    except: return None

def refine_summary_logic(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro'] if m in available_models), available_models[0])
        model = genai.GenerativeModel(selected_model)
        prompt = f"סכם את הפגישה לעברית עסקית (נושא, תקציר, החלטות ומשימות):\n\n{raw_text}"
        return model.generate_content(prompt).text
    except Exception as e: return f"שגיאה בעיבוד: {e}"

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
# 2. טעינת נתונים והגדרות דף
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
    .record-row { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #f1f5f9; transition: background 0.2s; direction: rtl; }
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# ניהול State
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
    # --- דף פרויקט פנימי (ללא Fathom כפי שביקשת) ---
    p_name = st.session_state.selected_project
    st.markdown(f'<h1>{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear() 
        st.session_state.current_page = "main"
        st.rerun()
    st.info(f"ניהול פרויקט מפורט עבור {p_name}")

else:
    # --- דף דשבורד ראשי ---
    st.markdown('<h1 style="text-align:right;">Dashboard AI</h1>', unsafe_allow_html=True)
    
    # אזור כותרת ו-KPIs
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
    st.write(f"### {greeting}, סיון! | {now.strftime('%d/%m/%Y')}")

    col_right, col_left = st.columns([2, 1.2])

    with col_right:
        # פרויקטים
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'<div class="record-row"><a href="{p_url}" target="_self">📂 {row["project_name"]}</a><span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div>', unsafe_allow_html=True)

        # אז'ור
        with st.container(border=True):
            st.markdown("### 📋 משימות Azure")
            tasks = get_azure_tasks()
            for t in tasks:
                st.write(f"🔗 {t['fields']['System.Title']}")

    with col_left:
        # פגישות היום
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings_df[pd.to_datetime(meetings_df["date"]).dt.date == today]
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

        # תזכורות
        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
            if st.button("➕ תזכורת חדשה", use_container_width=True):
                st.session_state.adding_reminder = True

        # --- מיקום חדש: סיכומי Fathom (מתחת לתזכורות) ---
        with st.container(border=True):
            st.markdown("### ✨ סיכומי פגישות Fathom")
            f_meetings = get_fathom_meetings_auto()
            if not f_meetings:
                st.write("אין פגישות אחרונות.")
            else:
                for mtg in f_meetings:
                    r_id, r_title = mtg.get('recording_id'), mtg.get('title', 'פגישה')
                    s_key = f"sum_auto_{r_id}"
                    with st.expander(f"📅 {r_title}"):
                        if s_key not in st.session_state:
                            if st.button("צור סיכום 🪄", key=f"btn_{r_id}"):
                                raw = get_fathom_summary_raw(r_id)
                                if raw:
                                    st.session_state[s_key] = refine_summary_logic(raw)
                                    st.rerun()
                        else:
                            st.markdown(f'<div style="direction:rtl; text-align:right; background:#f9f9f9; padding:10px; border-radius:5px;">{st.session_state[s_key]}</div>', unsafe_allow_html=True)
                            if st.button("נקה 🗑️", key=f"del_{r_id}"):
                                del st.session_state[s_key]
                                st.rerun()
