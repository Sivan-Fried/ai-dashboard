import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS יציב ופשוט ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7; direction: rtl; }
    
    /* כותרת גרדיאנט מוקטנת */
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 20px;
    }

    /* המסגרת המעוצבת לאזורים - Gradient Border */
    .fancy-container {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2.5px solid transparent;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        color: #1f2a44;
    }

    /* רשומות פס תכלת */
    .record-box {
        background: #ffffff;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #edf2f7;
        border-right: 6px solid #4facfe;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* יישור לימין לכל מה שקשור לטקסט */
    h3, p, span, label { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל נמצאים בתיקייה"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()

# --- 4. כותרת ופרופיל ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

c1, c2, c3 = st.columns([1, 1, 2])
with c2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" style="width:130px; height:130px; border-radius:50%; object-fit: cover; object-position: center 20%; border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.1);"></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# KPI
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k_style = "background:white; padding:15px; border-radius:12px; text-align:center; box-shadow:0 2px 5px rgba(0,0,0,0.02);"
with k1: st.markdown(f"<div style='{k_style} border-top:4px solid #ff4b4b;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div style='{k_style} border-top:4px solid #ffa500;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div style='{k_style} border-top:4px solid #00c853;'>לפי התכנון 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div style='{k_style}'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 5. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # פרויקטים
    html_content = '<div class="fancy-container"><h3>📁 פרויקטים ומרכיבים</h3>'
    for _, row in projects.iterrows():
        html_content += f'<div class="record-box"><span><b>{row["project_name"]}</b></span><span style="color:gray; font-size:0.85em;">{row.get("project_type", "פרויקט")}</span></div>'
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)

    # AI Oracle
    st.markdown('<div class="fancy-container"><h3>✨ AI Oracle</h3>', unsafe_allow_html=True)
    a1, a2 = st.columns([1, 2])
    with a1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
    with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
    st.button("שגר שאילתה 🚀", use_container_width=True, key="ai_b")
    st.markdown('</div>', unsafe_allow_html=True)

with col_left:
    # פגישות
    html_meetings = '<div class="fancy-container"><h3>📅 פגישות היום</h3>'
    t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if t_m.empty: html_meetings += '<p>אין פגישות היום</p>'
    else:
        for _, r in t_m.iterrows():
            html_meetings += f'<div class="record-box"><span>📌 {r["meeting_title"]}</span></div>'
    html_meetings += '</div>'
    st.markdown(html_meetings, unsafe_allow_html=True)

    # תזכורות
    st.markdown('<div class="fancy-container"><h3>🔔 תזכורות</h3>', unsafe_allow_html=True)
    t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
    for _, row in t_r.iterrows():
        st.markdown(f'<div class="record-box"><span>🔔 {row["reminder_text"]}</span></div>', unsafe_allow_html=True)
    
    if st.button("➕ הוסף תזכורת", key="add_r"): st.session_state.add_mode = True
    if st.session_state.get("add_mode"):
        nt = st.text_input("משימה:", key="nt_i")
        if st.button("שמור", key="save_r"):
            st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([{"reminder_text": nt, "date": today}])], ignore_index=True)
            st.session_state.add_mode = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
