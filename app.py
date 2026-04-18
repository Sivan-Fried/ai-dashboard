import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS מוחלט ומתוקן ---
st.markdown("""
<style>
    /* רקע ויישור כללי */
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 25px !important;
    }

    /* פוקוס תמונה משופר */
    .profile-img {
        width: 140px; height: 140px; border-radius: 50% !important;
        object-fit: cover !important; 
        object-position: center 25% !important; /* פוקוס על הפנים */
        border: 4px solid white !important; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    /* מסגרת גרדיאנט עם גלילה פנימית */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2.5px solid transparent !important;
        border-radius: 20px !important;
        padding: 22px !important;
        background-color: white !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        max-height: 480px !important; /* גובה מקסימלי למכולה */
        overflow-y: auto !important; /* הפעלת גלילה */
    }

    /* עיצוב רשומות */
    .record-row {
        background: #ffffff !important;
        padding: 12px 18px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 6px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.85em; font-weight: 600; background: #f0f9ff; padding: 4px 10px; border-radius: 6px; }
    .tag-orange { color: #d97706; font-size: 0.85em; font-weight: 600; background: #fffbeb; padding: 4px 10px; border-radius: 6px; }

    /* יישור טקסט ואלמנטים */
    h3, p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
    
    .stButton>button { width: 100% !important; border-radius: 10px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state:
    st.session_state.rem_live = reminders.copy()
if "show_add" not in st.session_state:
    st.session_state.show_add = False

# --- 4. כותרת ופרופיל ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
with p3:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. דשבורד מרכזי ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # פרויקטים
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            st.markdown(f'<div class="record-row"><span style="font-weight:bold;">📂 {row["project_name"]}</span><span class="tag-blue">{row.get("project_type", "פרויקט")}</span></div>', unsafe_allow_html=True)

    # AI Oracle
    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
        st.button("שגר שאילתה 🚀", key="ai_btn")

with col_left:
    # פגישות
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="record-row"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    # תזכורות
    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        
        for _, row in t_r.iterrows():
            p_name = row.get('project_name', 'כללי')
            st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{p_name}</span></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # כפתור הוספה
        if not st.session_state.show_add:
            if st.button("➕ הוסף תזכורת", key="open_add"):
                st.session_state.show_add = True
                st.rerun()
        else:
            # שורת הוספה Inline
            st.markdown("---")
            c1, c2, c3 = st.columns([1.5, 1.2, 0.5])
            with c1: nt = st.text_input("משימה", label_visibility="collapsed", placeholder="מה לעשות?", key="nt_f")
            with c2: np = st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="np_f")
            with c3:
                if st.button("✅", key="sv_f"):
                    if nt:
                        new_r = pd.DataFrame([{"reminder_text": nt, "date": today, "project_name": np}])
                        st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_r], ignore_index=True)
                        st.session_state.show_add = False
                        st.rerun()
            if st.button("ביטול", key="cl_f"):
                st.session_state.show_add = False
                st.rerun()
