import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS - החזרת הצבע והגרדיאנט למסגרות
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; direction: rtl; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* עיצוב המלבן היוקרתי עם הגרדיאנט - וידוא שהעיצוב נשמר */
    .fancy-container {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        direction: rtl;
        text-align: right;
    }

    .list-item {
        background: #fdfdfd;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e0e6ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        height: 85px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .stSelectbox, .stTextInput, .stButton {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# 2. פונקציות ונתונים
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

# 3. כותרת ופרופיל
st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><h2 style='font-weight:800;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>ניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

col_h1, col_h2, col_h3 = st.columns([1, 1, 2])
with col_h2:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:120px; height:120px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover; object-position: center top;"></div></div>', unsafe_allow_html=True)
with col_h3:
    st.markdown(f'<div style="margin-top:25px; text-align:right;"><h3>{greeting}, סיון!</h3><p style="color:gray;">{now.strftime("%d/%m/%Y | %H:%M")}</p></div>', unsafe_allow_html=True)

# רווח מוגדל (60px) בין הפרופיל ל-KPI
st.markdown("<div style='margin-bottom:60px;'></div>", unsafe_allow_html=True)

# 4. KPI
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:3px solid red;'><p style='color:gray; margin:0;'>בסיכון 🔴</p><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:3px solid orange;'><p style='color:gray; margin:0;'>במעקב 🟡</p><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:3px solid green;'><p style='color:gray; margin:0;'>בתקין 🟢</p><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><p style='color:gray; margin:0;'>סה\"כ</p><b>{len(projects)}</b></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. גוף הדשבורד - חלוקה לטורים
col_main, col_side = st.columns([2, 1.2])

with col_main:
    # מלבן פרויקטים
    icons_map = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
    p_html = ""
    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        p_html += f'<div class="list-item"><span>{dot}</span><div style="flex-grow:1;"><b>{icons_map.get(row["project_type"], "📁")} {row["project_name"]}</b> <small style="color:gray;">| {row["project_type"]}</small></div></div>'
    st.markdown(f'<div class="fancy-container"><h3 style="margin-top:0;">📁 פרויקטים ומרכיבים</h3>{p_html}</div>', unsafe_allow_html=True)

    # מלבן AI Oracle - מעוצב ומכיל את כל האלמנטים
    st.markdown('<div class="fancy-container"><h3 style="margin-top:0;">✨ AI Oracle</h3>', unsafe_allow_html=True)
    c_ai1, c_ai2, c_ai3 = st.columns([1, 1.5, 0.5])
    with c_ai1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
    with c_ai2: st.text_input("שאלה", placeholder="שאל את ה-AI...", label_visibility="collapsed", key="ai_q")
    with c_ai3: 
        if st.button("🚀", use_container_width=True, key="ai_go"): st.info("מנתח...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    # מלבן פגישות
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    m_html = "".join([f'<div class="list-item">📌 <b>{r["meeting_title"]}</b></div>' for _, r in today_m.iterrows()])
    st.markdown(f'<div class="fancy-container"><h3 style="margin-top:0;">📅 פגישות היום</h3>{m_html if m_html else "אין פגישות"}</div>', unsafe_allow_html=True)

    # מלבן תזכורות - מעוצב עם פרויקט והוספה מהירה
    st.markdown('<div class="fancy-container"><h3 style="margin-top:0;">🔔 תזכורות</h3>', unsafe_allow_html=True)
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    
    for _, row in today_r.iterrows():
        st.markdown(f"""
        <div class="list-item">
            🔔 <div style="flex-grow:1;"><b>{row['reminder_text']}</b><br><small style="color:#4facfe;">פרויקט: {row['project_name']}</small></div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("➕ הוסף תזכורת", key="add_btn"): st.session_state.show_add = True
    
    if st.session_state.get("show_add"):
        ra, rb, rc = st.columns([1.5, 1, 0.6])
        with ra: nt = st.text_input("מה להזכיר?", label_visibility="collapsed", key="nt")
        with rb: np = st.selectbox("למי?", projects["project_name"].tolist(), label_visibility="collapsed", key="np")
        with rc: 
            if st.button("✅"):
                if nt:
                    new_r = {"reminder_text": nt, "project_name": np, "date": today}
                    st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_r])], ignore_index=True)
                    st.session_state.show_add = False
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
