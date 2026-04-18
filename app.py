import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS חסין
st.set_page_config(layout="wide", page_title="Dashboard AI - ניהול פרויקטים")

st.markdown("""
<style>
    /* רקע כללי */
    body, .stApp { background-color: #f2f4f7; }
    
    /* טקסט מדורג לכותרת */
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* עיצוב ה-KPI למעלה - יציב ונקי */
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #eef0f2;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* המלבן המאוחד של הפרויקטים (התיקייה הלבנה) */
    .unified-project-box {
        background-color: white;
        border: 1px solid #e6e9ef;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        direction: rtl;
        text-align: right;
        margin: 20px 0;
    }

    /* שורת פרויקט בודד בתוך המלבן */
    .project-item {
        background: #f9fafb;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #f0f2f5;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* עיצוב כללי של כרטיסים (לפגישות ותזכורות) */
    .status-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #eee;
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<div style='text-align:center; margin-bottom:30px;'><h1 style='direction:rtl;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>לניהול פרויקטים</span></h1></div>", unsafe_allow_html=True)

# 2. טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינת הקבצים: {e}")
    st.stop()

# 3. KPI - חלק עליון
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><small>סה״כ פרויקטים</small><h2>{len(projects)}</h2></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top: 4px solid red;'><small>בסיכון 🔴</small><h2 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h2></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top: 4px solid orange;'><small>במעקב 🟡</small><h2 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h2></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top: 4px solid green;'><small>לפי התכנון 🟢</small><h2 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. אזור הפרויקטים - "המלבן המאוחד"
# בניית רשימת הפרויקטים כ-HTML מראש
project_list_html = ""
icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}

for _, row in projects.iterrows():
    icon = icons.get(row['project_type'], "📁")
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    project_list_html += f"""
    <div class="project-item">
        <span style="font-size:18px;">{dot}</span>
        <div style="flex-grow:1; margin-right:15px; text-align:right;">
            <b>{icon} {row['project_name']}</b> 
            <span style="color:gray; font-size:12px; margin-right:8px;">| {row['project_type']}</span>
        </div>
    </div>
    """

# הזרקת המלבן הלבן שכולל גם את הכותרת וגם את הרשימה
st.markdown(f"""
<div class="unified-project-box">
    <h3 style="margin-top:0; border-bottom:1px solid #f2f4f7; padding-bottom:15px; color:#1f2a44;">📁 פרויקטים ומרכיבים</h3>
    <div style="margin-top:15px;">
        {project_list_html}
    </div>
</div>
""", unsafe_allow_html=True)

# 5. פגישות ותזכורות
col_r, col_l = st.columns(2)

with col_r:
    st.markdown("<h3 style='text-align:right;'>📅 פגישות היום</h3>", unsafe_allow_html=True)
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.info("אין פגישות היום")
    else:
        for _, row in today_m.iterrows():
            st.markdown(f"<div class='status-card'>📌 <b>{row['meeting_title']}</b><br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)

with col_l:
    st.markdown("<h3 style='text-align:right;'>🔔 תזכורות</h3>", unsafe_allow_html=True)
    today_r = reminders[pd.to_datetime(reminders["date"]).dt.date == today]
    with st.container(height=220):
        if today_r.empty: st.info("אין תזכורות 🎉")
        else:
            for _, row in today_r.iterrows():
                st.markdown(f"<div class='status-card'>🔔 {row['reminder_text']}</div>", unsafe_allow_html=True)

# 6. AI Oracle
st.markdown("---")
st.markdown("### ✨ AI Oracle")
c1, c2 = st.columns([1, 2])
with c1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="ai_sel")
with c2: st.text_input("שאלה לניתוח", key="ai_q")
if st.button("בצע ניתוח"):
    st.info("מנתח נתונים...")
