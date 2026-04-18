import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS חסין
st.set_page_config(layout="wide", page_title="Dashboard AI")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* המלבן הלבן שביקשת - רק לכותרת */
    .title-box {
        background-color: white;
        border: 1px solid #e6e9ef;
        border-radius: 12px;
        padding: 15px 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
    }

    /* שורת פרויקט נקייה מתחת למלבן */
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

    /* KPI יציבים */
    .kpi-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<div style='text-align:center; margin-bottom:20px;'><h2 style='direction:rtl;'><span class='text-gradient'>Dashboard AI</span></h2></div>", unsafe_allow_html=True)

# 2. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("שגיאה בטעינת נתונים"); st.stop()

# 3. KPI (חלק עליון)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><small>פרויקטים</small><h3>{len(projects)}</h3></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:3px solid red;'>🔴<h3>{len(projects[projects['status']=='אדום'])}</h3></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:3px solid orange;'>🟡<h3>{len(projects[projects['status']=='צהוב'])}</h3></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top:3px solid green;'>🟢<h3>{len(projects[projects['status']=='ירוק'])}</h3></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. אזור הפרויקטים
# המלבן שביקשת - רק הכותרת בפנים
st.markdown("""
<div class="title-box">
    <h3 style="margin:0;">📁 פרויקטים ומרכיבים</h3>
</div>
""", unsafe_allow_html=True)

# רשימת הפרויקטים מתחת למלבן
icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
for _, row in projects.iterrows():
    icon = icons.get(row['project_type'], "📁")
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    st.markdown(f"""
    <div class="project-row">
        <span style="font-size:18px;">{dot}</span>
        <div style="flex-grow:1; margin-right:15px; text-align:right;">
            <b>{icon} {row['project_name']}</b> | <small style="color:gray;">{row['project_type']}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. לו"ז ו-AI
st.markdown("---")
c_r, c_l = st.columns(2)
with c_r:
    st.markdown("### 📅 פגישות היום")
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    for _, row in today_m.iterrows():
        st.info(f"📌 {row['meeting_title']} ({row['time']})")

with c_l:
    st.markdown("### ✨ סוכן AI")
    st.selectbox("פרויקט", projects["project_name"].tolist(), key="p_ai")
    st.text_input("שאלה לבוט", key="q_ai")
