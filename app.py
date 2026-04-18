import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב
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

    .kpi-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .project-row {
        background: white;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #eee;
        direction: rtl;
        text-align: right;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }

    .card {
        background: white; 
        padding: 15px; 
        border-radius: 10px;
        margin-bottom: 10px; 
        border: 1px solid #eee;
        direction: rtl; 
        text-align: right;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# כותרת
st.markdown("<div style='text-align:center; margin-bottom:20px;'><h2 style='font-weight:800; direction:rtl;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>לניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

# 2. פרופיל
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
        st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_base64}" style="width:140px; height:140px; border-radius:50%; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1); object-fit:cover;"></div>', unsafe_allow_html=True)

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
with k2: st.markdown(f"<div class='kpi-card' style='border-top:3px solid red;'><p>בסיכון 🔴</p><h4 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h4></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:3px solid orange;'><p>במעקב 🟡</p><h4 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h4></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top:3px solid green;'><p>לפי התכנון 🟢</p><h4 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h4></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים - המבנה המקורי
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)

# המלבן הלבן שכולל רק את הכותרת
with st.container(border=True):
    st.markdown("<h3 style='margin:0;'>📁 פרויקטים ומרכיבים</h3>", unsafe_allow_html=True)

# הרשימה זורמת מתחתיו בתוך ה-Section הצבעוני
def type_icon(ptype):
    icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
    return icons.get(ptype, "📁")

for _, row in projects.iterrows():
    icon = type_icon(row["project_type"])
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    st.markdown(f"""
    <div class="project-row">
        <span style="float:left;">{dot}</span>
        <div>
            {icon} <b>{row['project_name']}</b> 
            <span style="color:gray; font-size:12px; margin-right:10px;">| {row['project_type']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 6. לו"ז ותזכורות
c_right, c_left = st.columns(2)
with c_right:
    st.markdown("### 📅 פגישות היום")
    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_meetings.empty: st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"<div class='card'>📌 {row['meeting_title']}<br>🕒 {row['time']}<br>📁 {row['project_name']}</div>", unsafe_allow_html=True)

with c_left:
    st.markdown("### 🔔 תזכורות")
    today_reminders = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    with st.container(height=260):
        if today_reminders.empty: st.info("אין תזכורות 🎉")
        else:
            for _, row in today_reminders.iterrows():
                icon = "🤖" if row["source"] == "ai" else "✍️"
                st.markdown(f"<div class='card'>{icon} {row['reminder_text']} | 📁 {row['project_name']}</div>", unsafe_allow_html=True)

# 7. AI האורקל
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'><h3>✨ סוכן ה-AI שלך</h3>", unsafe_allow_html=True)
api_key = st.secrets.get("GEMINI_API_KEY")
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_sel")
with ca2: q_in = st.text_input("מה תרצי לדעת?", key="q_in")

if st.button("בצע ניתוח"):
    if q_in:
        st.info("מנתח נתונים...")
st.markdown("</div>", unsafe_allow_html=True)
