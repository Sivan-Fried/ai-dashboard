import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS
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

    /* עיצוב המלבן הלבן המאוחד (מבוסס על הקונטיינר של סטריםליט) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #eee !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }

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

    .project-card {
        background:#fcfcfc; 
        padding:10px; 
        border-radius:8px; 
        margin-bottom:8px; 
        border: 1px solid #f0f0f0;
        direction: rtl;
        text-align: right;
    }

    .card {
        background: white; 
        padding: 15px; 
        border-radius: 10px;
        margin-bottom: 10px; 
        border: 1px solid #eee;
        direction: rtl; 
        text-align: right;
    }

    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    
    h3 { color: #1f2a44; margin: 0 0 15px 0; direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<div style='text-align:center; margin-bottom:20px;'><h2 style='font-weight:800; direction:rtl;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>לניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

# 2. פרופיל ותמונה
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

l, c, r = st.columns([1.2, 1, 1.2])
with l: st.markdown(f'<div style="direction:rtl; text-align:right; margin-top:40px;"><h3>{greeting}, סיון!</h3><p style="color:gray;">{now.strftime("%d/%m/%Y %H:%M")}</p></div>', unsafe_allow_html=True)
with c:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center; margin-top:10px;"><div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover;"></div></div>', unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה: {e}"); st.stop()

if "reminders_live" not in st.session_state: st.session_state.reminders_live = reminders.copy()

# 4. KPI
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><p>סה״כ פרויקטים</p><h4>{len(projects)}</h4></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid red;'><p>בסיכון 🔴</p><h4 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h4></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid orange;'><p>במעקב 🟡</p><h4 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h4></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid green;'><p>לפי התכנון 🟢</p><h4 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h4></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים - התיקייה המאוחדת
# העטיפה הצבעונית החיצונית
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)

# המלבן הלבן הפנימי (Container) שמכיל כותרת + רשימה
with st.container(border=True):
    st.markdown("<h3>📁 פרויקטים ומרכיבים</h3>", unsafe_allow_html=True)
    
    def type_icon(ptype):
        icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
        return icons.get(ptype, "📁")

    for _, row in projects.iterrows():
        icon = type_icon(row["project_type"])
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        
        # הדפסת כל שורה כאלמנט HTML נקי
        st.markdown(f"""
        <div class="project-card">
            <span style="float:left;">{dot}</span>
            <span>{icon} <b>{row['project_name']}</b> | <small style="color:gray;">{row['project_type']}</small></span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 6. לו"ז ותזכורות
col_r, col_l = st.columns(2)
with col_r:
    st.markdown("### 📅 פגישות היום")
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.info("אין פגישות היום")
    else:
        for _, row in today_m.iterrows():
            st.markdown(f"<div class='card'>📌 {row['meeting_title']}<br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)

with col_l:
    st.markdown("### 🔔 תזכורות")
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    with st.container(height=250):
        for _, row in today_r.iterrows():
            st.markdown(f"<div class='card'>🔔 {row['reminder_text']}</div>", unsafe_allow_html=True)

# 7. AI
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'><h3>✨ AI Oracle</h3>", unsafe_allow_html=True)
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist())
with ca2: q_in = st.text_input("שאלה ל-AI")
if st.button("ניתוח"):
    st.write("מנתח נתונים...")
st.markdown("</div>", unsafe_allow_html=True)
