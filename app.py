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
# 1. הגדרות דף ועיצוב (CSS) - גרסת יצירה סופית ומדויקת
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
    
    div[data-testid="stVerticalBlockBorderWrapper"], .st-emotion-cache-1ne20ew {
        background: white !important;
        border-radius: 18px !important;
        padding: 15px !important;
    }

    /* עיצוב רשומה סטנדרטי (פרויקטים, אז'ור, פגישות) */
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

    /* תיקון אזור פאטום - Expander שמתנהג כרשומה לחיצה */
    .fathom-fix .stExpander { border: none !important; background: transparent !important; margin-bottom: 4px !important; }
    .fathom-fix .stExpander summary {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        flex-direction: row-reverse !important; /* טקסט בימין, חץ בשמאל */
        align-items: center !important;
        list-style: none !important;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .fathom-fix .stExpander summary:hover {
        border-color: #4facfe !important;
        background-color: #f8fafc !important;
    }
    .fathom-fix .stExpander summary svg { display: none !important; } /* העלמת החץ המקורי */
    .fathom-fix .stExpander summary::after {
        content: 'chevron_left';
        font-family: 'Material Symbols Rounded';
        color: #94a3b8;
        font-size: 20px;
        margin-right: auto;
    }

    /* כפתורי תזכורת באותה שורה */
    div[data-testid="column"] button { height: 38px !important; margin-top: 0px !important; width: 100% !important; }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    .kpi-card { background: white; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    .project-link { text-decoration: none !important; color: inherit !important; display: block !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. לוגיקה (זהה לחלוטין לקוד המקור שלך)
# =========================================================
def get_azure_tasks():
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post("https://dev.azure.com/amandigital/_apis/wit/wiql?api-version=6.0", 
                            json={"query": "SELECT [System.Id], [System.Title], [System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New'"}, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/amandigital/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject,System.CreatedDate&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    try:
        res = requests.get("https://api.fathom.ai/external/v1/meetings", headers={"X-Api-Key": st.secrets["FATHOM_API_KEY"]})
        return res.json().get('items', [])[:5], 200
    except: return [], 500

def refine_with_ai(text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"סכם לעברית עסקית רהוטה: {text}").text
    except: return "שגיאה ב-AI"

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "current_page" not in st.session_state: st.session_state.current_page = "main"

# =========================================================
# 3. ניווט ודף פרויקט
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
                # ה-Roadmap המלא והמקורי שלך
                roadmap_html = """<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap" rel="stylesheet"><style>body { font-family: 'Assistant', sans-serif; background-color: white; margin: 0; padding: 0; overflow: hidden; }.timeline-wrapper { position: relative; width: 1000px; margin: 50px auto; height: 200px; display: flex; justify-content: space-between; align-items: flex-end; padding: 0 50px; }.main-line { position: absolute; bottom: 6px; left: 0; right: 0; height: 1px; background: #cbd5e1; z-index: 1; }.today-indicator { position: absolute; bottom: -15px; right: 525px; display: flex; flex-direction: column; align-items: center; z-index: 5; }.today-line { width: 2px; height: 60px; border-left: 2px dashed #bfdbfe; }.today-text { color: #3b82f6; font-size: 11px; font-weight: 700; margin-bottom: 4px; }.item { display: flex; flex-direction: column; align-items: center; width: 90px; z-index: 3; position: relative; }.card { background: white; padding: 4px 6px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; text-align: center; width: 100%; margin-bottom: 8px; }.connector { width: 1px; height: 15px; background: #e2e8f0; }.dot { width: 12px; height: 12px; background: #475569; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 1px #475569; z-index: 4; }.tag { font-size: 8px; font-weight: 700; padding: 1px 4px; border-radius: 2px; display: inline-block; margin-bottom: 2px; }.amit { background: #eff6ff; color: #1e40af; }.measy { background: #f5f3ff; color: #5b21b6; }.soch { background: #ecfdf5; color: #065f46; }.date { font-size: 13px; font-weight: 600; color: #1e293b; margin: 0; }.status { font-size: 8px; font-weight: 700; margin-top: 2px; }.live { color: #10b981; } .wip { color: #f59e0b; }</style></head><body><div class="timeline-wrapper"><div class="main-line"></div><div class="today-indicator"><span class="today-text">היום 20.04</span><div class="today-line"></div></div><div class="item"><div class="card"><span class="tag amit">עמיתים</span><div class="date">08.03</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag measy">מעסיקים</span><div class="date">08.03</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag soch">סוכנים</span><div class="date">24.03</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag amit">עמיתים</span><div class="date">10.04</div><span class="status live">LIVE</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag amit">עמיתים</span><div class="date">יולי</div><span class="status wip">WIP</span></div><div class="connector"></div><div class="dot"></div></div><div class="item"><div class="card"><span class="tag measy">מעסיקים</span><div class="date">TBD</div><span class="status" style="color:#94a3b8">HOLD</span></div><div class="connector"></div><div class="dot"></div></div></div></body></html>"""
                components.html(roadmap_html, height=300)
            else: st.info(f"תוכנית עבודה עבור {p_name} תעודכן בהמשך.")

# =========================================================
# 4. דשבורד ראשי
# =========================================================
else:
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    # Header & KPIs
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    st.markdown(f"<h3 style='text-align:center;'>שלום סיון | {now.strftime('%H:%M')}</h3>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>2</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>1</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>5</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([1, 1])

    with col_right:
        # פרויקטים
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'<a href="{p_url}" target="_self" class="project-link"><div class="record-row"><b>📂 {row["project_name"]}</b><span class="material-symbols-rounded" style="color:#94a3b8;">chevron_left</span></div></a>', unsafe_allow_html=True)

        # אז'ור
        with st.container(border=True):
            st.markdown("### 📋 משימות באז'ור")
            tasks = get_azure_tasks()
            for t in tasks:
                st.markdown(f'<div class="record-row"><span>🔗 {t["fields"]["System.Title"]}</span><span class="tag-orange">{t["fields"]["System.TeamProject"]}</span></div>', unsafe_allow_html=True)

        # AI
        with st.container(border=True):
            st.markdown("### ✨ עוזר AI")
            q = st.text_input("שאלה לגבי הדאטה", key="ai_q", placeholder="מה תרצי לדעת?")
            if st.button("שגר 🚀", use_container_width=True): st.info("מנתח...")

    with col_left:
        # תזכורות
        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row["project_name"]}</span></div>', unsafe_allow_html=True)
            
            if st.session_state.get("adding_reminder", False):
                # תיקון: שורה אחת
                c1, c2, c3, c4 = st.columns([1, 1.5, 0.4, 0.4])
                with c1: n_p = st.selectbox("פ", ["כללי"] + projects["project_name"].tolist(), label_visibility="collapsed")
                with c2: n_t = st.text_input("ת", placeholder="תזכורת", label_visibility="collapsed")
                with c3: 
                    if st.button("✅"):
                        if n_t: st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"date": today, "reminder_text": n_t, "project_name": n_p}])])
                        st.session_state.adding_reminder = False; st.rerun()
                with c4:
                    if st.button("❌"): st.session_state.adding_reminder = False; st.rerun()
            else:
                if st.button("➕", use_container_width=True): st.session_state.adding_reminder = True; st.rerun()

        # פאטום עם התיקון הסופי
        st.markdown('<div class="fathom-fix">', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### ✨ סיכומי פגישות Fathom")
            items, status = get_fathom_meetings()
            if status == 200:
                for mtg in items:
                    with st.expander(f"📅 {mtg.get('title', 'פגישה')}"):
                        if st.button("סכם ב-AI 🪄", key=mtg['recording_id'], use_container_width=True):
                            st.write("מעבד...")
        st.markdown('</div>', unsafe_allow_html=True)
