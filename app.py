import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב (הגרסה היציבה והמאוחדת)
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* מעטפת חיצונית עם מסגרת גרדיאנט */
    .section-wrap {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        direction: rtl;
        text-align: right;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* עיצוב המלבן הלבן הפנימי שביקשת (חל על st.container עם border) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #eee !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }

    /* KPI מוקטן (כפי שתיקנו) */
    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    .kpi-card h4 { margin: 0; padding: 0; font-size: 1.2rem; }
    .kpi-card p { margin: 0; font-size: 0.9rem; color: #666; }

    /* רשומות מקוריות */
    .project-card {
        background: white; 
        padding: 10px; 
        border-radius: 8px;
        margin-bottom: 6px; 
        border: 1px solid #f0f0f0;
        direction: rtl; 
        text-align: right;
    }

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

# 2. פרופיל ותמונה
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב" if 18 <= now.hour < 22 else "לילה טוב"

left, center, right = st.columns([1.2, 1, 1.2])
with left:
    st.markdown(f'<div style="direction:rtl; text-align:right; margin-top:40px;"><div style="font-size:22px;">{greeting}, סיון!</div><div style="font-size:13px; color:gray;">{now.strftime("%d/%m/%Y %H:%M")}</div></div>', unsafe_allow_html=True)
with center:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center; margin-top:10px;"><div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover;"></div></div>', unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("שגיאה בטעינת קבצי אקסל")
    st.stop()

# 4. KPI - הגרסה המוקטנת
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><p>סה״כ פרויקטים</p><h4>{len(projects)}</h4></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid red;'><p>בסיכון 🔴</p><h4 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h4></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid orange;'><p>במעקב 🟡</p><h4 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h4></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid green;'><p>לפי התכנון 🟢</p><h4 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h4></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים - האזור עם התיחום הלבן הפנימי
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
st.markdown("<h3>📁 פרויקטים</h3>", unsafe_allow_html=True)

# שימוש ב-container של Streamlit כמלבן הלבן - זו הדרך היחידה שלא שוברת את הדף
with st.container(border=True):
    def type_icon(ptype):
        return {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}.get(ptype, "📁")

    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        st.markdown(f"""
        <div class="project-card">
            {type_icon(row['project_type'])} {row['project_name']}
            <span style="color:gray; font-size:12px;"> | {row['project_type']}</span>
            <span style="float:left;">{dot}</span>
        </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 6. לו"ז ותזכורות
col_r, col_l = st.columns(2)
with col_r:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 📅 פגישות היום")
    with st.container(border=True):
        t_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_meetings.empty: st.info("אין פגישות היום")
        else:
            for _, r in t_meetings.iterrows():
                st.markdown(f"<div class='project-card'>📌 {r['meeting_title']}<br><small>{r['time']} | {r['project_name']}</small></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_l:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 🔔 תזכורות")
    with st.container(border=True):
        t_rem = reminders[pd.to_datetime(reminders["date"]).dt.date == today]
        if t_rem.empty: st.info("אין תזכורות היום")
        else:
            for _, r in t_rem.iterrows():
                st.markdown(f"<div class='project-card'>🔔 {r['reminder_text']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 7. AI האורקל
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'>", unsafe_allow_html=True)
st.markdown("### ✨ סוכן ה-AI שלך")
with st.container(border=True):
    ca1, ca2 = st.columns([1, 2])
    with ca1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_sel")
    with ca2: st.text_input("מה תרצי לדעת?", key="q_in")
st.markdown("</div>", unsafe_allow_html=True)
