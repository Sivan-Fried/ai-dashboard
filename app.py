import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב יציב
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

    /* מעטפת חיצונית עם גרדיאנט */
    .section-wrap {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
        direction: rtl;
        text-align: right;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* התיחום הלבן הפנימי שביקשת - "אזור התוכן" */
    .inner-content-area {
        background-color: #ffffff;
        border: 1px solid #eef0f2;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }

    /* KPI מוקטן ואלגנטי */
    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    .kpi-card h4 { margin: 0; font-size: 1.1rem; color: #1f2a44; }
    .kpi-card p { margin: 0; font-size: 0.85rem; color: #666; }

    /* רשומות (פרויקטים/פגישות) */
    .list-item {
        background: #fdfdfd; 
        padding: 10px 15px; 
        border-radius: 8px;
        margin-bottom: 6px; 
        border: 1px solid #f0f0f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    }

    h3 { color: #1f2a44; text-align: right; direction: rtl; margin-top: 0; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית מוקטנת
st.markdown("""
<div style="text-align:center; margin-bottom:15px;">
    <h2 style="font-weight:800; direction:rtl; font-size: 1.7rem;">
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
    st.markdown(f'<div style="direction:rtl; text-align:right; margin-top:30px;"><div style="font-size:20px; font-weight:600;">{greeting}, סיון!</div><div style="font-size:12px; color:gray;">{now.strftime("%d/%m/%Y %H:%M")}</div></div>', unsafe_allow_html=True)
with center:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:120px; height:120px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 8px 20px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover;"></div></div>', unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("שגיאה בטעינת קבצי האקסל")
    st.stop()

# 4. KPI - 4 עמודות מעוצבות
k1, k2, k3, k4 = st.columns(4)
stats = [
    (k1, "סה״כ פרויקטים", len(projects), "none"),
    (k2, "בסיכון 🔴", len(projects[projects['status']=='אדום']), "red"),
    (k3, "במעקב 🟡", len(projects[projects['status']=='צהוב']), "orange"),
    (k4, "לפי התכנון 🟢", len(projects[projects['status']=='ירוק']), "green")
]
for col, label, val, color in stats:
    border_style = f"border-top: 3px solid {color};" if color != "none" else ""
    col.markdown(f"<div class='kpi-card' style='{border_style}'><p>{label}</p><h4>{val}</h4></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים - האזור עם התיחום הלבן הפנימי
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
st.markdown("<h3>📁 רשימת פרויקטים</h3>", unsafe_allow_html=True)
st.markdown("<div class='inner-content-area'>", unsafe_allow_html=True)

def get_p_icon(p_type):
    return {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}.get(p_type, "📁")

for _, row in projects.iterrows():
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    st.markdown(f"""
    <div class="list-item">
        <span>{get_p_icon(row['project_type'])} <b>{row['project_name']}</b> <small style="color:gray;">| {row['project_type']}</small></span>
        <span>{dot}</span>
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# 6. לו"ז ותזכורות
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 📅 פגישות היום")
    st.markdown("<div class='inner-content-area'>", unsafe_allow_html=True)
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.info("אין פגישות להיום")
    else:
        for _, r in today_m.iterrows():
            st.markdown(f"<div class='list-item'><span>📌 {r['meeting_title']}</span><small>{r['time']}</small></div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)
    st.markdown("### 🔔 תזכורות")
    st.markdown("<div class='inner-content-area'>", unsafe_allow_html=True)
    # כאן נשאר ה-Container המקורי של Streamlit לתזכורות כדי לאפשר גלילה
    t_rem = reminders[pd.to_datetime(reminders["date"]).dt.date == today]
    if t_rem.empty: st.write("אין תזכורות חדשות")
    else:
        for _, r in t_rem.iterrows():
            st.markdown(f"<div class='list-item'>🔔 {r['reminder_text']}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# 7. AI האורקל
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'>", unsafe_allow_html=True)
st.markdown("### ✨ סוכן ה-AI שלך")
st.markdown("<div class='inner-content-area'>", unsafe_allow_html=True)
ca1, ca2 = st.columns([1, 2])
with ca1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_sel")
with ca2: st.text_input("מה תרצי לדעת?", key="q_in")
if st.button("נתח נתונים"):
    st.info("מנתח בעזרת Gemini...")
st.markdown("</div></div>", unsafe_allow_html=True)
