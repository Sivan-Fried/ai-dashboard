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

# --- 2. CSS - יישור לימין ותיקון ויזואלי ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; text-align: right !important; }
    
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    .kpi-card {
        background: white !important; padding: 15px !important; border-radius: 12px !important;
        text-align: right !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        direction: rtl !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; margin-top: 5px; }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 1.5px solid transparent !important;
        border-radius: 18px !important;
        padding: 15px !important;
        background-color: white !important;
    }

    /* תיבת ניתוח AI */
    .ai-response-box {
        background: #f0f9ff;
        border-right: 5px solid #4facfe;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        color: #1e3a8a;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    h3, p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# פונקציית רשימה נגללת
def render_scrollable_list(df, is_reminder=False):
    rows_html = ""
    for _, row in df.iterrows():
        label = row.get('project_name', 'כללי')
        text = row['reminder_text'] if is_reminder else row['project_name']
        icon = "🔔" if is_reminder else "📂"
        rows_html += f"""
        <div style="background:white; padding:10px; border-radius:10px; margin-bottom:8px; 
                    border:1px solid #edf2f7; border-right:5px solid #4facfe; display:flex; 
                    justify-content:space-between; align-items:center; direction:rtl; text-align:right;">
            <span>{icon} {text}</span>
            <span style="color:#4facfe; font-size:0.8em; background:#f0f9ff; padding:2px 8px; border-radius:5px;">{label}</span>
        </div>
        """
    full_html = f'<div style="max-height:280px; overflow-y:auto; padding:5px; direction:rtl;">{rows_html}</div>'
    return st.components.v1.html(full_html, height=300)

# --- 3. טעינה ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Data Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()
if "show_add" not in st.session_state: st.session_state.show_add = False
if "ai_analysis" not in st.session_state: st.session_state.ai_analysis = None

# --- 4. כותרת ופרופיל ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    img = get_base64_image("profile.png")
    if img: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img}" class="profile-img"></div>', unsafe_allow_html=True)
with p3:
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    st.markdown(f"<div style='margin-top:20px;'><h3>שלום סיון!</h3><p>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

# --- 6. גוף ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        render_scrollable_list(projects)

    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        sel_p = st.selectbox("בחר פרויקט לניתוח", projects["project_name"].tolist(), key="ai_p")
        q_text = st.text_input("שאלה ל-AI", placeholder="מה הסטטוס העדכני של הפרויקט?", key="ai_i")
        
        if st.button("שגר שאילתה 🚀", use_container_width=True):
            if q_text:
                with st.spinner("מנתח נתונים..."):
                    time.sleep(1.5) # סימולציה של מחשבה
                    st.session_state.ai_analysis = f"**ניתוח עבור {sel_p}:** על סמך הנתונים האחרונים, הפרויקט נמצא במגמת שיפור. מומלץ להתמקד בשלב האישור הסופי מול הלקוח בשבוע הבא."
            else:
                st.warning("נא להזין שאלה")
        
        # הצגת הניתוח אם קיים
        if st.session_state.ai_analysis:
            st.markdown(f'<div class="ai-response-box">{st.session_state.ai_analysis}</div>', unsafe_allow_html=True)

with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; border-right:5px solid #4facfe; margin-bottom:8px;">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        render_scrollable_list(t_r, is_reminder=True)
        
        if not st.session_state.show_add:
            if st.button("➕ הוסף תזכורת", use_container_width=True):
                st.session_state.show_add = True
                st.rerun()
        else:
            new_t = st.text_input("משימה:")
            new_p = st.selectbox("פרויקט:", projects["project_name"].tolist())
            if st.button("✅ שמור"):
                new_entry = pd.DataFrame([{"reminder_text": new_t, "date": today, "project_name": new_p}])
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_entry], ignore_index=True)
                st.session_state.show_add = False
                st.rerun()
