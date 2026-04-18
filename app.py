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

# --- 2. CSS סופי - יישור ימין, KPI לבן, וגלילה קשיחה ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stApp { background-color: #f2f4f7 !important; }
    
    /* כותרת */
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important; font-size: 2.2rem !important; font-weight: 800; margin-bottom: 20px;
    }

    /* תמונה */
    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    /* KPI - לבן נקי בלי תכלת */
    .kpi-card {
        background: white !important; padding: 15px !important; border-radius: 12px !important;
        text-align: center !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important; border: none !important;
    }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }

    /* קונטיינרים עם בורדר דק */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important; border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important; border-radius: 18px !important; padding: 15px !important;
    }

    /* שורות רשימה */
    .record-row {
        background: #f8fafc; padding: 10px 15px; border-radius: 10px; margin-bottom: 8px;
        border: 1px solid #edf2f7; display: flex; justify-content: space-between; align-items: center;
        direction: rtl; text-align: right;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }

    h3, p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    div[data-testid="stWidgetLabel"] { justify-content: flex-start !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. נתונים וניהול מצב (Session State) ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()
if "ai_analysis" not in st.session_state: st.session_state.ai_analysis = ""

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
    # פרויקטים עם גלילה
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        with st.container(height=300, border=False):
            for _, row in projects.iterrows():
                st.markdown(f'<div class="record-row"><span>📂 {row["project_name"]}</span><span class="tag-blue">{row.get("project_type", "פרויקט")}</span></div>', unsafe_allow_html=True)

    # AI Oracle - עובד ומתעדכן
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: sel_p = st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with a2: q_in = st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
        
        if st.button("שגר שאילתה 🚀", use_container_width=True):
            if q_in:
                with st.spinner("מנתח..."):
                    time.sleep(1)
                    st.session_state.ai_analysis = f"**ניתוח AI עבור {sel_p}:** הפרויקט נמצא במצב יציב. מומלץ לעקוב אחר אבני הדרך של שבוע הבא."
                    st.rerun()
            else: st.warning("נא להזין שאלה")
        
        if st.session_state.ai_analysis:
            st.info(st.session_state.ai_analysis)

with col_left:
    # פגישות
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    # תזכורות - הוספה בשורה אחת וגלילה
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        
        # שורת הוספה מהירה
        c1, c2 = st.columns([3, 1])
        with c1: new_txt = st.text_input("תזכורת חדשה...", label_visibility="collapsed", key="quick_rem")
        with c2: 
            if st.button("הוסף", use_container_width=True) and new_txt:
                new_data = pd.DataFrame([{"reminder_text": new_txt, "date": today, "project_name": "כללי"}])
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_data], ignore_index=True)
                st.rerun()

        # אזור גלילה לתזכורות
        with st.container(height=250, border=False):
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)
