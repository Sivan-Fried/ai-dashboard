import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות בסיסיות ---
st.set_page_config(layout="wide", page_title="Dashboard AI", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS גלובלי (יישור ורקע) ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* יישור טקסט ואלמנטים לימין בצורה גורפת */
    [data-testid="stVerticalBlock"] { direction: rtl !important; }
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label {
        text-align: right !important; direction: rtl !important;
    }
    
    /* עיצוב כותרת גרדיאנט ראשית */
    .main-title {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }

    /* עיצוב KPI */
    .kpi-card {
        background: white; padding: 15px; border-radius: 12px;
        text-align: center; border: 1px solid #e0e6ed;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* עיצוב פריטי רשימה */
    .list-item {
        background: #fdfdfd; padding: 10px; border-radius: 10px;
        margin-bottom: 8px; border: 1px solid #eee;
        display: flex; align-items: center; gap: 10px;
    }

    /* הזרקת העיצוב למכולות של Streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל קיימים"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()

# --- 4. Header & Profile ---
st.markdown('<h1 class="main-title">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

col_p1, col_p2, col_p3 = st.columns([1, 1, 2])
with col_p2:
    if img_b64:
        st.markdown(f'''
            <div style="display:flex; justify-content:center;">
                <div style="width:130px; height:130px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;">
                </div>
            </div>''', unsafe_allow_html=True)
with col_p3:
    st.markdown(f"<div style='margin-top:25px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI Row ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:4px solid red;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:4px solid orange;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:4px solid green;'>בתקין 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 6. גוף ה-Dashboard ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
            st.markdown(f'<div class="list-item"><span>{dot}</span><b>{row["project_name"]}</b></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        # כל רכיבי ה-AI בתוך המכולה המעוצבת
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="sel_ai")
        with a2: st.text_input("שאלה ל-AI", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="txt_ai")
        st.button("שגר שאילתה 🚀", use_container_width=True)

with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="list-item">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        today_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        with st.container(height=180, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f'<div class="list-item">🔔 {row["reminder_text"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("➕ הוסף תזכורת"): st.session_state.add_task = True
        if st.session_state.get("add_task"):
            nt = st.text_input("מה המשימה?", key="new_t")
            if st.button("✅ שמור"):
                new_r = {"reminder_text": nt, "date": today}
                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([new_r])], ignore_index=True)
                st.session_state.add_task = False
                st.rerun()
