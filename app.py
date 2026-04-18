import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS מקיף (יישור לימין ועיצוב כרטיסים)
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
    
    /* תיקון יישור לכל האלמנטים של Streamlit */
    .stMarkdown, .stText, div[data-testid="stBlock"] {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<div style='text-align:center; margin-bottom:20px;'><h2 style='font-weight:800; direction:rtl;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>לניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

# 2. פונקציית תמונה ופרופיל (פוקוס מקורי)
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

l, c, r = st.columns([1.2, 1, 1.2])
with l: 
    st.markdown(f'<div style="direction:rtl; text-align:right; margin-top:40px; color:#1f2a44;"><div style="font-size:22px; font-weight:bold;">{greeting}, סיון!</div><div style="font-size:14px; color:gray;">{now.strftime("%d/%m/%Y %H:%M")}</div></div>', unsafe_allow_html=True)
with c:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:5px solid white; box-shadow:0 10px 25px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover;"></div></div>', unsafe_allow_html=True)

st.markdown("---")

# 3. טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינת קבצים: {e}"); st.stop()

if "reminders_live" not in st.session_state: 
    st.session_state.reminders_live = reminders.copy()

# 4. אזור ה-KPI (סידור מחדש יציב)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><p style='color:gray; margin:0;'>סה״כ פרויקטים</p><h3 style='margin:5px 0;'>{len(projects)}</h3></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:3px solid red;'><p style='color:gray; margin:0;'>בסיכון 🔴</p><h3 style='color:red; margin:5px 0;'>{len(projects[projects['status']=='אדום'])}</h3></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:3px solid orange;'><p style='color:gray; margin:0;'>במעקב 🟡</p><h3 style='color:orange; margin:5px 0;'>{len(projects[projects['status']=='צהוב'])}</h3></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top:3px solid green;'><p style='color:gray; margin:0;'>לפי התכנון 🟢</p><h3 style='color:green; margin:5px 0;'>{len(projects[projects['status']=='ירוק'])}</h3></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים (המלבן המאוחד לכותרת)
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("<h3 style='margin:0; text-align:right;'>📁 פרויקטים ומרכיבים</h3>", unsafe_allow_html=True)

def type_icon(ptype):
    icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
    return icons.get(ptype, "📁")

for _, row in projects.iterrows():
    icon = type_icon(row["project_type"])
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

# 6. לו"ז ותזכורות (כולל כפתור הוספה)
col_right, col_left = st.columns(2)

with col_right:
    st.markdown("### 📅 פגישות היום")
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.info("אין פגישות היום")
    else:
        for _, row in today_m.iterrows():
            st.markdown(f"<div class='card'>📌 <b>{row['meeting_title']}</b><br>🕒 {row['time']}<br>📁 {row['project_name']}</div>", unsafe_allow_html=True)

with col_left:
    st.markdown("### 🔔 תזכורות")
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    
    with st.container(height=280):
        if today_r.empty: st.info("אין תזכורות להיום")
        else:
            for _, row in today_r.iterrows():
                icon = "🤖" if row["source"] == "ai" else "✍️"
                st.markdown(f"<div class='card'>{icon} {row['reminder_text']} | 📁 {row['project_name']}</div>", unsafe_allow_html=True)
    
    # מנגנון הוספת תזכורת
    if st.button("➕ הוספת תזכורת"):
        st.session_state.add_mode = True
    
    if st.session_state.get("add_mode"):
        with st.form("new_reminder"):
            t_text = st.text_input("מה התזכורת?")
            t_proj = st.selectbox("שיוך לפרויקט", projects["project_name"].tolist())
            if st.form_submit_button("שמור"):
                new_row = {"reminder_text": t_text, "project_name": t_proj, "date": today, "source": "manual"}
                st.session_state.reminders_live.loc[len(st.session_state.reminders_live)] = new_row
                st.session_state.add_mode = False
                st.rerun()

# 7. AI האורקל
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'><h3>✨ סוכן ה-AI שלך</h3>", unsafe_allow_html=True)
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_ai")
with ca2: q_in = st.text_input("מה תרצי לדעת?", key="q_ai")
if st.button("בצע ניתוח"):
    st.info("המערכת מנתחת את נתוני הפרויקט...")
st.markdown("</div>", unsafe_allow_html=True)
