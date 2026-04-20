import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ועיצוב (הגרסה המקורית שלך ללא שינוי) ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

# ייבוא האייקונים רק עבור החץ
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
    .record-row {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. לוגיקה ונתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders_df
if "current_page" not in st.session_state: st.session_state.current_page = "main"
if "selected_project" not in st.session_state: st.session_state.selected_project = None
if "ai_response" not in st.session_state: st.session_state.ai_response = ""

# --- 3. תצוגה ---
if st.session_state.current_page == "project":
    st.markdown(f'<h1 class="dashboard-header">{st.session_state.selected_project}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.session_state.current_page = "main"; st.rerun()
    st.info(f"מציג נתונים עבור פרויקט {st.session_state.selected_project}")

else:
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    
    p1, p2, p3 = st.columns([1, 1, 2])
    with p2:
        if img_b64: st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
    with p3: st.markdown(f"<div><h3 style='margin-bottom:0;'>שלום, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    for col, (label, color) in zip([k1, k2, k3, k4], [("בסיכון 🔴", "אדום"), ("במעקב 🟡", "צהוב"), ("תקין 🟢", "ירוק"), ("סה\"כ פרויקטים", "all")]):
        count = len(projects) if color == "all" else len(projects[projects["status"]==color])
        col.markdown(f'<div class="kpi-card">{label}<br><b>{count}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_right, col_left = st.columns([2, 1.2])

    with col_right:
        # אזור פרויקטים - עבודה עם פינצטה
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            with st.container(height=350, border=False):
                for _, row in projects.iterrows():
                    # יצירת מכלול לכל שורה
                    container = st.container()
                    with container:
                        # 1. העיצוב הויזואלי המקורי שלך + תוספת החץ
                        st.markdown(f'''
                            <div class="record-row" style="position: relative; margin-bottom: 0px;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <b>📂 {row["project_name"]}</b>
                                    <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                                </div>
                                <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span>
                            </div>
                        ''', unsafe_allow_html=True)
                        
                        # 2. כפתור שקוף שיושב בדיוק מעל הרשומה
                        # ה-margin-top השלילי גורם לו "לצוף" מעל ה-div הקודם
                        if st.button("", key=f"p_{row['project_name']}", help=f"לחץ לצפייה ב{row['project_name']}", use_container_width=True):
                            st.session_state.selected_project = row['project_name']
                            st.session_state.current_page = "project"
                            st.rerun()
                        
                        # הזרקת CSS מקומי רק לכפתור השקוף של הפרויקטים כדי לא להרוס כפתורים אחרים
                        st.markdown(f"""
                            <style>
                            div[data-testid="stHorizontalBlock"] div:has(button[key="p_{row['project_name']}"]) button {{
                                background: transparent !important;
                                border: none !important;
                                color: transparent !important;
                                height: 50px !important;
                                margin-top: -58px !important;
                                position: relative !important;
                                z-index: 10 !important;
                                cursor: pointer !important;
                            }}
                            </style>
                        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
            a1, a2 = st.columns([1, 2])
            sel_p = a1.selectbox("פרויקט", projects["project_name"].tolist(), key="ai_p", label_visibility="collapsed")
            q_in = a2.text_input("שאלה", placeholder="מה תרצי לדעת?", key="ai_i", label_visibility="collapsed")
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                st.session_state.ai_response = f"ניתוח עבור {sel_p}..."
            if st.session_state.ai_response: st.info(st.session_state.ai_response)

    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty: st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
            for _, row in t_r.iterrows():
                st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
