import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS "בלתי שביר"
st.set_page_config(layout="wide", page_title="ניהול פרויקטים")

st.markdown("""
<style>
    /* עיצוב כללי ויישור לימין */
    .stApp { background-color: #f2f4f7; direction: rtl; }
    
    /* מציאת המכולות של Streamlit והזרקת העיצוב לתוכן */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        direction: rtl !important;
    }

    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* עיצוב שורות ברשימה */
    .list-item {
        background: #fdfdfd;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 12px;
        direction: rtl;
    }

    /* יישור לימין לכל רכיב במערכת */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label, h3 {
        text-align: right !important;
        direction: rtl !important;
    }

    /* עיצוב כרטיסי ה-KPI העליונים */
    .kpi-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e0e6ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

# 2. נתונים ופונקציות
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל קיימים"); st.stop()

if "reminders_live" not in st.session_state: 
    st.session_state.reminders_live = reminders.copy()

# 3. ראש העמוד (Header)
st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h2 style='font-weight:800;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>ניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

col_h1, col_h2, col_h3 = st.columns([1, 1, 2])
with col_h2:
    if img_base64:
        # פוקוס תמונה גבוה יותר
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:130px; height:130px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover; object-position: 50% 15%;"></div></div>', unsafe_allow_html=True)
with col_h3:
    st.markdown(f'<div style="margin-top:25px;"><h3>{greeting}, סיון!</h3><p style="color:gray;">{now.strftime("%d/%m/%Y | %H:%M")}</p></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:50px;'></div>", unsafe_allow_html=True)

# 4. KPI Cards
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:3px solid red;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:3px solid orange;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:3px solid green;'>בתקין 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. הגוף המרכזי
col_main, col_side = st.columns([2, 1.2])

with col_main:
    # מלבן פרויקטים
    with st.container(border=True):
        st.subheader("📁 פרויקטים ומרכיבים")
        for _, row in projects.iterrows():
            dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
            st.markdown(f'<div class="list-item"><span>{dot}</span><div style="flex-grow:1;"><b>{row["project_name"]}</b> <small style="color:gray;">| {row["project_type"]}</small></div></div>', unsafe_allow_html=True)

    # מלבן AI Oracle
    with st.container(border=True):
        st.subheader("✨ AI Oracle")
        ca1, ca2, ca3 = st.columns([1, 1.5, 0.5])
        with ca1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with ca2: st.text_input("שאלה", placeholder="שאל את ה-AI...", label_visibility="collapsed", key="ai_q")
        with ca3: 
            if st.button("🚀", key="ai_go"): st.info("מנתח...")

with col_side:
    # מלבן פגישות
    with st.container(border=True):
        st.subheader("📅 פגישות היום")
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="list-item">📌 <b>{r["meeting_title"]}</b></div>', unsafe_allow_html=True)

    # מלבן תזכורות עם גלילה והוספה
    with st.container(border=True):
        st.subheader("🔔 תזכורות")
        today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
        
        # יצירת אזור גלילה
        with st.container(height=220, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f"""
                <div class="list-item">
                    🔔 <div style="flex-grow:1;"><b>{row['reminder_text']}</b><br><small style="color:#4facfe;">{row['project_name']}</small></div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("➕ הוסף תזכורת", key="add_btn"): st.session_state.show_add = True
        
        if st.session_state.get("show_add"):
            ra, rb, rc = st.columns([1.5, 1, 0.6])
            with ra: nt = st.text_input("תזכורת", key="nt", label_visibility="collapsed")
            with rb: np = st.selectbox("פרויקט", projects["project_name"].tolist(), key="np", label_visibility="collapsed")
            with rc: 
                if st.button("✅"):
                    if nt:
                        new_r = {"reminder_text": nt, "project_name": np, "date": today}
                        st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_r])], ignore_index=True)
                        st.session_state.show_add = False
                        st.rerun()
