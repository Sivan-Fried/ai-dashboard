import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS
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

    /* מסגרת הפרויקטים */
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

    /* KPI קומפקטי ויציב */
    .kpi-container {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e0e6ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .kpi-title { color: gray; font-size: 13px; margin: 0; }
    .kpi-value { font-size: 22px; font-weight: bold; margin: 0; }

    .project-row {
        background: white;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
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

    .stMarkdown, .stText, div[data-testid="stBlock"] {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# 2. חלק עליון: פרופיל וברכה (מיקום תמונה וברכה)
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

st.markdown("<div style='text-align:center; margin-bottom:20px;'><h2 style='font-weight:800; direction:rtl;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>ניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

col_spacer_r, col_img, col_info, col_spacer_l = st.columns([1, 1, 2, 0.5])

with col_img:
    if img_base64:
        st.markdown(f"""
        <div style="display:flex; justify-content:center;">
            <div style="width:130px; height:130px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
                <img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover; object-position: center top;">
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_info:
    st.markdown(f"""
    <div style="direction:rtl; text-align:right; margin-top:30px;">
        <div style="font-size:24px; font-weight:bold; color:#1f2a44;">{greeting}, סיון!</div>
        <div style="font-size:14px; color:gray; margin-top:5px;">{now.strftime("%d/%m/%Y | %H:%M")}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("שגיאה בטעינת נתונים"); st.stop()

if "reminders_live" not in st.session_state: 
    st.session_state.reminders_live = reminders.copy()

# 4. KPI - סדר חדש (סטטוסים קודם, סך הכל בסוף)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-container' style='border-top:3px solid red;'><p class='kpi-title'>בסיכון 🔴</p><p class='kpi-value' style='color:red;'>{len(projects[projects['status']=='אדום'])}</p></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-container' style='border-top:3px solid orange;'><p class='kpi-title'>במעקב 🟡</p><p class='kpi-value' style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</p></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-container' style='border-top:3px solid green;'><p class='kpi-title'>בתקין 🟢</p><p class='kpi-value' style='color:green;'>{len(projects[projects['status']=='ירוק'])}</p></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-container'><p class='kpi-title'>סה\"כ פרויקטים</p><p class='kpi-value'>{len(projects)}</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("<h3 style='margin:0; text-align:right;'>📁 פרויקטים ומרכיבים</h3>", unsafe_allow_html=True)

icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
for _, row in projects.iterrows():
    icon = icons.get(row['project_type'], "📁")
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    st.markdown(f"""
    <div class="project-row">
        <span style="font-size:18px;">{dot}</span>
        <div style="text-align:right; flex-grow:1; margin-right:15px;">
            <b>{icon} {row['project_name']}</b> | <small style="color:gray;">{row['project_type']}</small>
        </div>
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
            st.markdown(f"<div class='card'>📌 <b>{row['meeting_title']}</b><br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)

with col_l:
    st.markdown("### 🔔 תזכורות")
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    with st.container(height=280):
        for _, row in today_r.iterrows():
            st.markdown(f"<div class='card'>🔔 {row['reminder_text']} | {row['project_name']}</div>", unsafe_allow_html=True)
    
    if st.button("➕ הוספת תזכורת"):
        st.session_state.add_mode = True
    
    if st.session_state.get("add_mode"):
        with st.form("new_rem"):
            t = st.text_input("תזכורת:")
            p = st.selectbox("פרויקט:", projects["project_name"].tolist())
            if st.form_submit_button("שמור"):
                st.session_state.reminders_live.loc[len(st.session_state.reminders_live)] = {"reminder_text": t, "project_name": p, "date": today, "source": "manual"}
                st.session_state.add_mode = False
                st.rerun()

# 7. AI Oracle
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'><h3>✨ AI Oracle</h3>", unsafe_allow_html=True)
ca1, ca2 = st.columns([1, 2])
with ca1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_ai")
with ca2: st.text_input("שאלה לניתוח", key="q_ai")
if st.button("בצע ניתוח"): st.info("מנתח נתונים...")
st.markdown("</div>", unsafe_allow_html=True)
