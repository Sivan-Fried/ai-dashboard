import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב (השיטה היציבה - CSS על אלמנטים קיימים)
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    
    /* גרדיאנט לכותרת */
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* תיחום אזור צבעוני (המסגרת החיצונית) */
    .section-wrap {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        direction: rtl;
        text-align: right;
    }

    /* עיצוב ה-Container של Streamlit שייראה כמלבן לבן פנימי */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #eee !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    /* רשומות פנימיות */
    .project-row {
        background: #fff; 
        padding: 10px; 
        border-radius: 8px; 
        margin-bottom: 6px; 
        border: 1px solid #f0f0f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    }

    /* KPI */
    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    .kpi-card h4 { margin: 0; font-size: 1.2rem; }
    .kpi-card p { margin: 0; font-size: 0.9rem; color: #666; }

    h3 { color: #1f2a44; text-align: right; direction: rtl; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית מוקטנת
st.markdown("""
<div style="text-align:center; margin-bottom:20px;">
    <h2 style="font-weight:800; direction:rtl; font-size: 1.8rem;">
        <span class="text-gradient">Dashboard AI</span>
        <span style="color: #1f2a44;">לניהול פרויקטים</span>
    </h2>
</div>
""", unsafe_allow_html=True)

# 2. נתונים (טעינה בסיסית)
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("לא נמצאו קבצי הנתונים")
    st.stop()

if "reminders_live" not in st.session_state:
    st.session_state.reminders_live = reminders.copy()

# 3. KPI - 4 עמודות
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><p>סה״כ פרויקטים</p><h4>{len(projects)}</h4></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid red;'><p>בסיכון 🔴</p><h4 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h4></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid orange;'><p>במעקב 🟡</p><h4 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h4></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid green;'><p>לפי התכנון 🟢</p><h4 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h4></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. אזור הפרויקטים - התיקון המבוקש
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
st.markdown("<h3>📁 פרויקטים</h3>", unsafe_allow_html=True)

# שימוש ב-container של Streamlit כמלבן הלבן
with st.container(border=True):
    def get_icon(ptype):
        icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
        return icons.get(ptype, "📁")

    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        st.markdown(f"""
        <div class="project-row">
            <span>{get_icon(row['project_type'])} <b>{row['project_name']}</b> <small style="color:gray;">| {row['project_type']}</small></span>
            <span>{dot}</span>
        </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 5. לו"ז ותזכורות
c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 📅 פגישות היום")
    with st.container(border=True):
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f"📌 **{r['meeting_title']}** \n<small>{r['time']} | {r['project_name']}</small>", unsafe_allow_html=True)
                st.markdown("---")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 🔔 תזכורות")
    with st.container(border=True):
        t_rem = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
        for _, r in t_rem.iterrows():
            st.write(f"🔔 {r['reminder_text']}")
        
        if st.button("➕ הוספה"): st.session_state.add = True
        if st.session_state.get("add"):
            with st.form("add_rem"):
                txt = st.text_input("תזכורת:")
                if st.form_submit_button("✔"):
                    # לוגיקת הוספה כאן
                    st.session_state.add = False
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 6. AI
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'>", unsafe_allow_html=True)
st.markdown("### ✨ סוכן ה-AI שלך")
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist())
with ca2: q = st.text_input("מה תרצי לדעת?")
if st.button("נתח"):
    st.info("מבצע ניתוח...")
st.markdown("</div>", unsafe_allow_html=True)
