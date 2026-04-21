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

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 18px !important;
        padding: 15px !important;
    }

    /* רשומות פרויקטים - שחזור מקורי */
    .record-row {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        text-decoration: none !important;
        color: inherit !important;
    }

    /* פאטום - תיקון החץ לשמאל בלבד */
    .stExpander { border: none !important; background: transparent !important; margin-bottom: 5px !important; }
    .stExpander summary {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        flex-direction: row-reverse !important; /* דוחף אייקון לשמאל */
        align-items: center !important;
        list-style: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    .stExpander summary svg { display: none !important; } /* העלמת חץ מקורי */
    .stExpander summary::after {
        content: 'chevron_left';
        font-family: 'Material Symbols Rounded';
        color: #94a3b8;
        font-size: 20px;
        margin-right: auto;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    
    p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. נתונים ופונקציות (ללא שינוי)
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

# =========================================================
# 3. דף ראשי
# =========================================================

st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))

# Header
_, img_col, text_col = st.columns([1, 1, 2])
with img_col:
    if img_b64: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_b64}" style="width:130px; height:130px; border-radius:50%; border:4px solid white; object-fit:cover;"></div>', unsafe_allow_html=True)
with text_col: st.markdown(f"<h3>שלום, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([1, 1])

with col_right:
    # פרויקטים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים")
        for _, row in projects.iterrows():
            p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
            st.markdown(f'''
                <a href="{p_url}" target="_self" class="record-row">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <b>📂 {row["project_name"]}</b>
                        <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                    </div>
                    <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span>
                </a>
            ''', unsafe_allow_html=True)

    # AI
    with st.container(border=True):
        st.markdown("### ✨ עוזר AI")
        a1, a2 = st.columns([1, 2])
        a1.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed")
        a2.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed")
        st.button("שגר שאילתה 🚀", use_container_width=True)

with col_left:
    # תזכורות
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        for _, row in t_r.iterrows():
            st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
        
        if st.session_state.adding_reminder:
            # תיקון: שורה אחת ללא קפיצה
            r1, r2, r3, r4 = st.columns([1.2, 2.5, 0.4, 0.4])
            with r1: st.selectbox("בחר", ["כללי"] + projects["project_name"].tolist(), label_visibility="collapsed", key="sel_p")
            with r2: st.text_input("מה להזכיר?", label_visibility="collapsed", key="rem_t")
            with r3: 
                if st.button("✅"):
                    if st.session_state.rem_t:
                        new_r = pd.DataFrame([{"date": today, "reminder_text": st.session_state.rem_t}])
                        st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_r], ignore_index=True)
                    st.session_state.adding_reminder = False; st.rerun()
            with r4:
                if st.button("❌"): st.session_state.adding_reminder = False; st.rerun()
        else:
            if st.button("➕ הוסף תזכורת", use_container_width=True):
                st.session_state.adding_reminder = True; st.rerun()

    # Fathom - תיקון סופי לחץ
    with st.container(border=True):
        st.markdown("### ✨ סיכומי Fathom")
        # דוגמה לרשומות פאטום
        f_items = [{"title": "סיכום ישיבת צוות", "date": "2026-04-20"}, {"title": "פגישת אפיון AI", "date": "2026-04-19"}]
        for item in f_items:
            with st.expander(f"📅 {item['title']} | {item['date']}"):
                st.write("כאן יופיע תוכן הסיכום...")
