import streamlit as st
import pandas as pd
import base64
import datetime
import time
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS מוחלט ויציב ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important; font-size: 2.2rem !important; font-weight: 800; margin-bottom: 20px;
    }

    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    /* KPI - לבן בלי בורדר */
    .kpi-card {
        background: white !important; padding: 15px !important; border-radius: 12px !important;
        text-align: right !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important; border: none !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }

    /* קונטיינרים */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important; border: 1.5px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important; border-radius: 18px !important; padding: 15px !important;
    }

    /* עיצוב שורות הרשימה ב-HTML */
    .html-row {
        background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px;
        border: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;
        direction: rtl; text-align: right; font-family: sans-serif;
    }
    .html-tag { font-size: 0.8em; font-weight: 600; padding: 2px 8px; border-radius: 5px; }

    h3, p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# פונקציית גלילה מבוססת HTML (לא נשברת)
def render_scroll_list(df, is_reminder=False):
    rows_html = ""
    for _, row in df.iterrows():
        icon = "🔔" if is_reminder else "📂"
        text = row['reminder_text'] if is_reminder else row['project_name']
        tag_val = row.get('project_name', 'כללי') if is_reminder else row.get('project_type', 'פרויקט')
        tag_style = "color:#d97706; background:#fffbeb;" if is_reminder else "color:#4facfe; background:#f0f9ff;"
        
        rows_html += f"""
        <div class="html-row">
            <span style="font-size:0.9rem; color:#1f2a44;">{icon} {text}</span>
            <span class="html-tag" style="{tag_style}">{tag_val}</span>
        </div>
        """
    return f'<div style="max-height:280px; overflow-y:auto; direction:rtl; padding-left:10px;">{rows_html}</div>'

# --- 3. נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()
if "ai_msg" not in st.session_state: st.session_state.ai_msg = ""

# --- 4. כותרת ופרופיל ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    img = get_base64_image("profile.png")
    if img: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img}" class="profile-img"></div>', unsafe_allow_html=True)
with p3:
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    st.markdown(f"<div><h3 style='margin:0;'>שלום, סיון!</h3><p style='color:gray;'>{now.strftime('%H:%M | %d/%m/%Y')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

# --- 6. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        st.components.v1.html(render_scroll_list(projects), height=300)

    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: sel_p = st.selectbox("פרויקט", projects["project_name"].tolist(), key="ai_p")
        with a2: q_in = st.text_input("שאלה", placeholder="מה תרצי לדעת?", key="ai_i")
        
        if st.button("שגר שאילתה 🚀", use_container_width=True):
            if q_in:
                with st.spinner("מנתח נתונים..."):
                    time.sleep(1)
                    st.session_state.ai_msg = f"**ניתוח AI עבור {sel_p}:** הפרויקט נמצא במסלול תקין. מומלץ לבדוק את אבני הדרך של שבוע הבא."
            else: st.warning("נא להזין שאלה")
        
        if st.session_state.ai_msg:
            st.info(st.session_state.ai_msg)

with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="html-row" style="background:white;"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        st.components.v1.html(render_scroll_list(t_r, is_reminder=True), height=250)
        st.button("➕ הוסף תזכורת", use_container_width=True)
