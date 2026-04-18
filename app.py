import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan")

# --- פונקציות עזר ---
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- CSS גלובלי (RTL וצבעים) ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7; direction: rtl; }
    [data-testid="stVerticalBlock"] { direction: rtl !important; }
    
    /* עיצוב ה-KPI */
    .kpi-card {
        background: white; padding: 15px; border-radius: 12px;
        text-align: center; border: 1px solid #e0e6ed;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* עיצוב רשימות */
    .list-item {
        background: #fdfdfd; padding: 12px; border-radius: 10px;
        margin-bottom: 10px; border: 1px solid #eee;
        display: flex; align-items: center; gap: 12px; text-align: right;
    }
    
    /* הכרחת יישור לימין לכל רכיבי המערכת */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label {
        text-align: right !important; direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# --- פונקציה גנרית למסגרת המעוצבת (עוטפת הכל) ---
def styled_card(title, icon=""):
    # הזרקת הסטייל ישירות למכולה שנוצרת
    st.markdown("""
        <style>
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
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        return st.container()

# --- טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("קובצי הנתונים חסרים"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()

# --- Header עם פוקוס תמונה מתוקן ---
st.markdown("<h1 style='text-align:center; color:#1f2a44;'>Dashboard AI</h1>", unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

col_p1, col_p2, col_p3 = st.columns([1, 1, 2])
with col_p2:
    if img_b64:
        # object-position: top דואג שהפוקוס יהיה על הפנים
        st.markdown(f'''
            <div style="display:flex; justify-content:center;">
                <div style="width:130px; height:130px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: top;">
                </div>
            </div>''', unsafe_allow_html=True)
with col_p3:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- KPI Section ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:4px solid red;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:4px solid orange;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:4px solid green;'>בתקין 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- גוף ה-Dashboard ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    with styled_card("פרויקטים ומרכיבים", "📁"):
        for _, row in projects.iterrows():
            dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
            st.markdown(f'<div class="list-item"><span>{dot}</span><b>{row["project_name"]}</b></div>', unsafe_allow_html=True)

    with styled_card("AI Oracle", "✨"):
        # כל רכיבי ה-AI בתוך המסגרת המעוצבת
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="sel_ai")
        with a2: st.text_input("שאלה ל-AI", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="txt_ai")
        st.button("שגר שאילתה 🚀", use_container_width=True)

with col_left:
    with styled_card("פגישות היום", "📅"):
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="list-item">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    with styled_card("תזכורות", "🔔"):
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
