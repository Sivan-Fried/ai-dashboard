import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS חסין
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    /* רקע כללי */
    body, .stApp { background-color: #f2f4f7; }
    
    /* טקסט מדורג */
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* מסגרת חיצונית צבעונית לאזורים */
    .outer-section {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }

    /* המלבן הלבן המאוחד (התיקייה) - עיצוב חסין */
    .unified-folder {
        background-color: white !important;
        border: 1px solid #eef0f2 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
        direction: rtl;
        text-align: right;
    }

    /* שורת פרויקט בודד */
    .project-entry {
        background: #f9fafb;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #f0f2f5;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    }

    /* כרטיסי KPI יציבים */
    .kpi-card-fixed {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #eef0f2;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* כרטיסי פגישות ותזכורות */
    .status-card {
        background: white;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #eee;
        direction: rtl;
        text-align: right;
    }
    
    h3, h4 { color: #1f2a44; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<div style='text-align:center; margin-bottom:30px;'><h1 style='font-weight:800; direction:rtl;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>ניהול פרויקטים</span></h1></div>", unsafe_allow_html=True)

# 2. נתונים (טעינה שקטה)
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("חסרים קבצי נתונים (Excel)"); st.stop()

# 3. KPI - בנייה ידנית למניעת שיבוש
cols = st.columns(4)
titles = ["סה״כ פרויקטים", "בסיכון 🔴", "במעקב 🟡", "לפי התכנון 🟢"]
colors = ["#1f2a44", "red", "orange", "green"]
counts = [
    len(projects),
    len(projects[projects['status']=='אדום']),
    len(projects[projects['status']=='צהוב']),
    len(projects[projects['status']=='ירוק'])
]

for i, col in enumerate(cols):
    with col:
        st.markdown(f"""
        <div class="kpi-card-fixed" style="border-top: 4px solid {colors[i]};">
            <p style="color:gray; margin:0; font-size:14px;">{titles[i]}</p>
            <h2 style="margin:5px 0; color:{colors[i]}; font-weight:800;">{counts[i]}</h2>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. אזור הפרויקטים - "התיקייה המאוחדת"
st.markdown("<div class='outer-section'>", unsafe_allow_html=True)

# בניית רשימת הפרויקטים ב-HTML
projects_list_html = ""
icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}

for _, row in projects.iterrows():
    icon = icons.get(row['project_type'], "📁")
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    projects_list_html += f"""
    <div class="project-entry">
        <span style="font-size:18px;">{dot}</span>
        <div style="text-align:right; flex-grow:1; margin-right:15px;">
            <span style="font-weight:600;">{icon} {row['project_name']}</span>
            <span style="color:gray; font-size:12px; margin-right:8px;">| {row['project_type']}</span>
        </div>
    </div>
    """

# הזרקת המלבן הלבן המאוחד (כותרת + רשימה)
st.markdown(f"""
<div class="unified-folder">
    <h3 style="margin-bottom:20px; border-bottom:1px solid #eee; padding-bottom:10px;">📁 פרויקטים ומרכיבים</h3>
    {projects_list_html}
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 5. פגישות ותזכורות
col_r, col_l = st.columns(2)

with col_r:
    st.markdown("<h3 style='text-align:right;'>📅 פגישות היום</h3>", unsafe_allow_html=True)
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.info("אין פגישות היום")
    else:
        for _, row in today_m.iterrows():
            st.markdown(f"<div class='status-card'><b>{row['meeting_title']}</b><br><small>{row['time']} | {row['project_name']}</small></div>", unsafe_allow_html=True)

with col_l:
    st.markdown("<h3 style='text-align:right;'>🔔 תזכורות</h3>", unsafe_allow_html=True)
    today_r = reminders[pd.to_datetime(reminders["date"]).dt.date == today]
    with st.container(height=200):
        for _, row in today_r.iterrows():
            st.markdown(f"<div class='status-card'>🔔 {row['reminder_text']}</div>", unsafe_allow_html=True)

# 6. AI Oracle
st.markdown("<div class='outer-section' style='border-right: 8px solid #4facfe;'>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-bottom:15px;'>✨ AI Oracle</h3>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 2])
with c1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="ai_p")
with c2: st.text_input("שאלה לניתוח", placeholder="מה הסטטוס של...", key="ai_q")
if st.button("שאל את הבוט"): st.info("מנתח נתונים...")
st.markdown("</div>", unsafe_allow_html=True)
