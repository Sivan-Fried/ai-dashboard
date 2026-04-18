import streamlit as st
import pandas as pd
import requests
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב (CSS נקי ויציב)
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

    /* כותרת האזורים */
    .section-header {
        color: #1f2a44;
        text-align: right;
        direction: rtl;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* KPI מוקטנים */
    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-card h4 { margin: 0; padding: 0; font-size: 1.1rem; }
    .kpi-card p { margin: 0; font-size: 0.85rem; color: #666; }

    /* עיצוב רשומה פנימית */
    .item-card {
        background: #fdfdfd;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 6px;
        border: 1px solid #f0f0f0;
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("""
<div style="text-align:center; margin-bottom:15px;">
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
    st.error("שגיאה בטעינת הנתונים")
    st.stop()

# 4. KPI - 4 עמודות (גרסה מוקטנת)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><p>סה״כ פרויקטים</p><h4>{len(projects)}</h4></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid red;'><p>בסיכון 🔴</p><h4 style='color:red;'>{len(projects[projects['status']=='אדום'])}</h4></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid orange;'><p>במעקב 🟡</p><h4 style='color:orange;'>{len(projects[projects['status']=='צהוב'])}</h4></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card' style='border-top: 3px solid green;'><p>לפי התכנון 🟢</p><h4 style='color:green;'>{len(projects[projects['status']=='ירוק'])}</h4></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים - עם תיחום (border=True)
st.markdown("<div class='section-header'>📁 פרויקטים</div>", unsafe_allow_html=True)
with st.container(border=True):
    def get_p_icon(p_type):
        return {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}.get(p_type, "📁")

    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        st.markdown(f"""
        <div class="item-card" style="display:flex; justify-content:space-between; align-items:center;">
            <span>{get_p_icon(row['project_type'])} {row['project_name']} <small style="color:gray;">| {row['project_type']}</small></span>
            <span>{dot}</span>
        </div>
        """, unsafe_allow_html=True)

# 6. לו"ז ותזכורות
col_r, col_l = st.columns(2)

with col_r:
    st.markdown("<div class='section-header'>📅 פגישות היום</div>", unsafe_allow_html=True)
    with st.container(border=True):
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.info("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f"<div class='item-card'>📌 {r['meeting_title']} <br><small>{r['time']} | {r['project_name']}</small></div>", unsafe_allow_html=True)

with col_l:
    st.markdown("<div class='section-header'>🔔 תזכורות</div>", unsafe_allow_html=True)
    with st.container(border=True):
        t_rem = reminders[pd.to_datetime(reminders["date"]).dt.date == today]
        scroll_area = st.container(height=180)
        with scroll_area:
            if t_rem.empty: st.write("אין תזכורות")
            else:
                for _, r in t_rem.iterrows():
                    st.markdown(f"<div class='item-card'>🔔 {r['reminder_text']}</div>", unsafe_allow_html=True)

# 7. AI האורקל
st.markdown("<br><div class='section-header'>✨ סוכן ה-AI שלך</div>", unsafe_allow_html=True)
with st.container(border=True):
    ca1, ca2 = st.columns([1, 2])
    with ca1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_sel")
    with ca2: st.text_input("מה תרצי לדעת?", key="q_in")
    if st.button("בצע ניתוח"):
        st.info("מנתח נתונים...")
