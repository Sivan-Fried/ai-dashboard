import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
import google.generativeai as genai

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

    /* רשומות פרויקטים - שחזור 1:1 */
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

    /* פאטום - תיקון החץ לשמאל */
    .stExpander { border: none !important; background: transparent !important; margin-bottom: 3px !important; }
    .stExpander summary {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        flex-direction: row !important; /* טקסט בימין */
        justify-content: space-between !important;
        align-items: center !important;
        list-style: none !important;
    }
    .stExpander summary svg { display: none !important; } /* הסרת החץ המקורי */
    .stExpander summary::before {
        content: 'chevron_left';
        font-family: 'Material Symbols Rounded';
        color: #94a3b8;
        font-size: 20px;
        order: -1; /* דוחף לשמאל */
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    
    /* עיצוב כפתורי אישור/ביטול בתזכורת */
    .rem-btn-col button {
        padding: 0px !important;
        height: 38px !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות (ללא שינוי)
# =========================================================

def get_azure_tasks():
    try:
        ORG_NAME = "amandigital"
        wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
        query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject], [System.CreatedDate] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject,System.CreatedDate&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    try:
        api_key = st.secrets["FATHOM_API_KEY"]
        headers = {"X-Api-Key": api_key, "Accept": "application/json"}
        response = requests.get("https://api.fathom.ai/external/v1/meetings", headers=headers, timeout=15)
        return response.json().get('items', [])[:5], response.status_code
    except: return [], 500

def get_fathom_summary(recording_id):
    try:
        api_key = st.secrets["FATHOM_API_KEY"]
        headers = {"X-Api-Key": api_key, "Accept": "application/json"}
        response = requests.get(f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary", headers=headers)
        return response.json().get("summary", {}).get("markdown_formatted")
    except: return None

# =========================================================
# 3. ניהול נתונים
# =========================================================
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False
if "current_page" not in st.session_state: st.session_state.current_page = "main"

# =========================================================
# 4. תצוגה
# =========================================================

if st.session_state.current_page == "main":
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    
    _, img_col, text_col = st.columns([1, 1, 2])
    with img_col:
        if img_b64: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with text_col: st.markdown(f"<h3>שלום, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([1, 1]) # חלוקה חצי-חצי

    with col_right:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'<a href="{p_url}" target="_self" style="text-decoration:none;"><div class="record-row"><div><b>📂 {row["project_name"]}</b> <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span></div><span class="material-symbols-rounded" style="color:#94a3b8; font-size:20px;">chevron_left</span></div></a>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<h3>📋 משימות Azure</h3>', unsafe_allow_html=True)
            tasks = get_azure_tasks()
            for t in tasks[:5]:
                f = t.get('fields', {})
                st.markdown(f'<div class="record-row"><span>🔗 {f.get("System.Title", "")[:35]}...</span><span class="tag-orange">{f.get("System.TeamProject", "")}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI")
            a1, a2 = st.columns([1, 2])
            sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed")
            q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed")
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                st.info(f"ניתוח עבור {sel_p} בביצוע...")

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span><span class="time-label">{r.get("start_time","")}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
            
            if st.session_state.adding_reminder:
                r_c1, r_c2, r_c3, r_c4 = st.columns([1.5, 3, 0.6, 0.6])
                new_p = r_c1.selectbox("פרויקט", projects["project_name"].tolist() + ["כללי"], label_visibility="collapsed")
                new_t = r_c2.text_input("תיאור", placeholder="מה להזכיר?", label_visibility="collapsed")
                with r_c3: 
                    if st.button("✅", key="save_rem"):
                        if new_t:
                            st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"date": today, "reminder_text": new_t, "project_name": new_p}])], ignore_index=True)
                            st.session_state.adding_reminder = False; st.rerun()
                with r_c4:
                    if st.button("❌", key="cancel_rem"):
                        st.session_state.adding_reminder = False; st.rerun()
            else:
                if st.button("➕ הוסף תזכורת", use_container_width=True):
                    st.session_state.adding_reminder = True; st.rerun()

        with st.container(border=True):
            st.markdown("### ✨ סיכומי Fathom")
            if 'f_data' not in st.session_state: st.session_state.f_data, _ = get_fathom_meetings()
            for mtg in st.session_state.f_data:
                with st.expander(f"📅 {mtg.get('title', 'פגישה')} | {mtg.get('recording_start_time', '')[:10]}"):
                    st.write("כאן יופיע הסיכון המופק מה-AI")
