import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS מינימלי וחסין
st.set_page_config(layout="wide", page_title="ניהול פרויקטים")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* מלבן הפרויקטים המאוחד */
    .projects-container {
        background-color: white;
        border: 1px solid #eee;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        margin: 20px 0;
        direction: rtl;
        text-align: right;
    }

    .project-line {
        background: #f9fafb;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #f0f2f5;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* עיצוב ה-KPI למניעת שיבוש */
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #eee;
    }

    .section-box {
        border-radius: 15px;
        padding: 20px;
        background: white;
        border: 1px solid #eee;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. כותרת ופרופיל
st.markdown("<div style='text-align:center;'><h1 style='direction:rtl;'><span class='text-gradient'>Dashboard AI</span></h1></div>", unsafe_allow_html=True)

try:
    projects = pd.read_excel("my_projects.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("לא נמצא קובץ אקסל")
    st.stop()

# 3. KPI - פשוט ונקי
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'>סה״כ פרויקטים<br><h2>{len(projects)}</h2></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='color:red;'>בסיכון 🔴<br><h2>{len(projects[projects['status']=='אדום'])}</h2></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='color:orange;'>במעקב 🟡<br><h2>{len(projects[projects['status']=='צהוב'])}</h2></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='color:green;'>בתקין 🟢<br><h2>{len(projects[projects['status']=='ירוק'])}</h2></div>", unsafe_allow_html=True)

# 4. המלבן המאוחד שביקשת (כותרת + פרויקטים)
# אני בונה את ה-HTML של הרשימה בנפרד כדי להכניס למלבן
project_rows_html = ""
icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}

for _, row in projects.iterrows():
    icon = icons.get(row['project_type'], "📁")
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    project_rows_html += f"""
    <div class="project-line">
        <span style="font-size:18px;">{dot}</span>
        <div style="flex-grow:1; margin-right:15px;">
            <b>{icon} {row['project_name']}</b> | <small>{row['project_type']}</small>
        </div>
    </div>
    """

# הזרקת המלבן המאוחד
st.markdown(f"""
<div class="projects-container">
    <h3 style="margin-bottom:20px; border-bottom:2px solid #f2f4f7; padding-bottom:10px;">📁 פרויקטים ומרכיבים</h3>
    {project_rows_html}
</div>
""", unsafe_allow_html=True)

# 5. לו"ז ו-AI (במבנה בסיסי כדי שלא יישבר)
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### 📅 פגישות ותזכורות")
    st.info("כאן יופיעו הפגישות שלך מהאקסל")

with col_b:
    st.markdown("### ✨ סוכן AI")
    st.selectbox("בחר פרויקט", projects["project_name"].tolist())
    st.text_input("שאלה לבוט")
