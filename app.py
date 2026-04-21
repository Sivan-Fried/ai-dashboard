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
# 1. הגדרות דף ועיצוב (CSS) - גרסת יצירה סופית
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan - גרסה יצירה", initial_sidebar_state="collapsed")

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
    
    h3 { font-size: 1.15rem !important; font-weight: 700; color: #1f2a44; text-align: right; }

    /* עיצוב רשומה כללית */
    .record-row {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 4px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        transition: all 0.2s ease;
    }
    .record-row:hover {
        border-color: #4facfe !important;
        background-color: #f8fafc !important;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.1) !important;
    }

    /* תיקון ספציפי לאזור הפאטום - Expander שמתחפש לרשומה */
    .fathom-container .stExpander { border: none !important; background: transparent !important; margin-bottom: 4px !important; }
    .fathom-container .stExpander summary {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        flex-direction: row-reverse !important; /* דוחף תוכן לימין וחץ לשמאל */
        align-items: center !important;
        list-style: none !important;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .fathom-container .stExpander summary:hover {
        border-color: #4facfe !important;
        background-color: #f8fafc !important;
    }
    .fathom-container .stExpander summary svg { display: none !important; } /* העלמת החץ המקורי */
    .fathom-container .stExpander summary::after {
        content: 'chevron_left';
        font-family: 'Material Symbols Rounded';
        color: #94a3b8;
        font-size: 20px;
        margin-right: auto;
    }

    /* יישור לחצנים בשורה אחת בתזכורת */
    .reminder-row-container { display: flex; align-items: center; gap: 5px; width: 100%; }
    div[data-testid="column"] button { height: 38px !important; margin-top: 0px !important; width: 100% !important; }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-family: monospace; }
    .profile-img { width: 130px; height: 130px; border-radius: 50%; border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .kpi-card { background: white; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    .project-link { text-decoration: none !important; color: inherit !important; display: block !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. לוגיקה ופונקציות (ללא שינוי)
# =========================================================
def get_azure_tasks():
    try:
        res = requests.post(f"https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", 
                            json={"query": "SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New'"}, 
                            auth=('', st.secrets["AZURE_PAT"]))
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/amandigital/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject&api-version=6.0", auth=('', st.secrets["AZURE_PAT"]))
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]}, timeout=10)
        return res.json().get('items', [])[:5], 200
    except: return [], 500

def refine_with_ai(text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"סכם לעברית עסקית: {text}").text
    except: return "שגיאה בסיכום ה-AI"

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Excel Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "current_page" not in st.session_state: st.session_state.current_page = "main"

# =========================================================
# 3. דף פרויקט (החזרתי בדיוק כפי שהיה)
# =========================================================
params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

if st.session_state.current_page == "project":
    p_name = st.session_state.selected_project
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה"):
        st.query_params.clear(); st.session_state.current_page = "main"; st.rerun()
    
    with st.container(border=True):
        st.markdown(f"### ℹ️ ניהול פרויקט: {p_name}")
        tab_work, tab_res, tab_risk, tab_meetings, tab_info = st.tabs(["📅 תוכנית עבודה", "👥 משאבים", "⚠️ סיכונים", "📝 סיכומי פגישות", "📊 מידע כללי"])
        with tab_work:
            if "אלטשולר" in p_name:
                roadmap_html = """<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="utf-8"><style>body { font-family: sans-serif; background: white; }.timeline-wrapper { position: relative; width: 900px; margin: 40px auto; height: 150px; display: flex; justify-content: space-between; align-items: flex-end; }.main-line { position: absolute; bottom: 10px; left: 0; right: 0; height: 2px; background: #cbd5e1; }.dot { width: 12px; height: 12px; background: #4facfe; border-radius: 50%; z-index: 2; }.card { background: #f8fafc; padding: 5px; border-radius: 5px; border: 1px solid #e2e8f0; text-align: center; font-size: 12px; margin-bottom: 10px; }</style></head><body><div class="timeline-wrapper"><div class="main-line"></div><div style="display:flex; flex-direction:column; align-items:center;"><div class="card">עמיתים<br>08.03</div><div class="dot"></div></div><div style="display:flex; flex-direction:column; align-items:center;"><div class="card">סוכנים<br>24.03</div><div class="dot"></div></div><div style="display:flex; flex-direction:column; align-items:center;"><div class="card">LIVE<br>יולי</div><div class="dot"></div></div></div></body></html>"""
                components.html(roadmap_html, height=250)
            else: st.info("תוכנית עבודה תעודכן בקרוב.")

# =========================================================
# 4. דשבורד ראשי
# =========================================================
else:
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    # Header & Profile
    c1, c2, c3 = st.columns([1, 1, 2])
    with c2:
        img = get_base64_image("profile.png")
        if img: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img}" class="profile-img"></div>', unsafe_allow_html=True)
    with c3:
        now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
        st.markdown(f"### שלום סיון, {now.strftime('%H:%M')}")

    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val in zip([k1, k2, k3, k4], ["בסיכון 🔴", "במעקב 🟡", "תקין 🟢", 'סה"כ'], [2, 1, 5, 8]):
        col.markdown(f'<div class="kpi-card">{label}<br><b>{val}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([1, 1])

    with col_right:
        # פרויקטים
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'<a href="{p_url}" target="_self" class="project-link"><div class="record-row"><div><b>📂 {row["project_name"]}</b></div><span class="material-symbols-rounded" style="color:#94a3b8;">chevron_left</span></div></a>', unsafe_allow_html=True)

        # AI Assistant
        with st.container(border=True):
            st.markdown("### ✨ עוזר AI")
            q = st.text_input("שאלה לגבי הפרויקטים", placeholder="מה תרצי לדעת?")
            if st.button("שגר 🚀", use_container_width=True): st.info("מנתח נתונים...")

    with col_left:
        # תזכורות
        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row["project_name"]}</span></div>', unsafe_allow_html=True)
            
            if st.session_state.get("adding_reminder", False):
                r_c1, r_c2, r_c3, r_c4 = st.columns([1, 2, 0.4, 0.4])
                with r_c1: n_p = st.selectbox("פ", ["כללי"] + projects["project_name"].tolist(), label_visibility="collapsed")
                with r_c2: n_t = st.text_input("ת", placeholder="מה להזכיר?", label_visibility="collapsed")
                with r_c3: 
                    if st.button("✅"): 
                        if n_t: 
                            st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"date": today, "reminder_text": n_t, "project_name": n_p}])])
                        st.session_state.adding_reminder = False; st.rerun()
                with r_c4: 
                    if st.button("❌"): st.session_state.adding_reminder = False; st.rerun()
            else:
                if st.button("➕", use_container_width=True): st.session_state.adding_reminder = True; st.rerun()

        # פאטום - העיצוב המתוקן
        st.markdown('<div class="fathom-container">', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### ✨ סיכומי פגישות Fathom")
            items, status = get_fathom_meetings()
            if status == 200:
                for mtg in items:
                    with st.expander(f"📅 {mtg.get('title', 'פגישה')}"):
                        st.write("כאן יופיע סיכום הפגישה לאחר לחיצה על כפתור ה-AI.")
                        if st.button("סכם ב-AI 🪄", key=mtg['recording_id']): st.write("מעבד...")
        st.markdown('</div>', unsafe_allow_html=True)
