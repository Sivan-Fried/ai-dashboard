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

    /* המלבן הלבן המאוחד שביקשת - הגדרה ידנית חסינה */
    .unified-project-box {
        background-color: white !important;
        border: 1px solid #eee !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
    }

    .project-item {
        background:#fcfcfc; 
        padding:10px; 
        border-radius:8px; 
        margin-bottom:6px; 
        border: 1px solid #eee;
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

    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-card h4 { margin: 0; padding: 0; font-size: 1.2rem; }
    .kpi-card p { margin: 0; font-size: 0.9rem; color: #666; }

    h3 { color: #1f2a44; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<div style='text-align:center; margin-bottom:20px;'><h2 style='font-weight:800; direction:rtl;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>לניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

# 2. פונקציית תמונה ופרופיל
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב" if 18 <= now.hour < 22 else "לילה טוב"

left, center, right = st.columns([1.2, 1, 1.2])
with left: st.markdown(f'<div style="direction:rtl; text-align:right; margin-top:40px; color:#1f2a44;"><div style="font-size:22px;">{greeting}, סיון!</div><div style="font-size:13px; color:gray;">{now.strftime("%d/%m/%Y %H:%M")}</div></div>', unsafe_allow_html=True)
with center:
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

# 5. פרויקטים - המלבן המאוחד (כותרת + רשימה)
st.markdown("<div class='section-wrap'>", unsafe_allow_html=True)

# בניית ה-HTML של הפרויקטים מראש
project_list_html = ""
def type_icon(ptype):
    icons = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
    return icons.get(ptype, "📁")

for _, row in projects.iterrows():
    icon = type_icon(row["project_type"])
    dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
    project_list_html += f"""
    <div class="project-item">
        {icon} <b>{row['project_name']}</b> 
        <span style="color:gray; font-size:12px;"> | {row['project_type']}</span>
        <span style="float:left;">{dot}</span>
    </div>
    """

# הזרקה של המלבן המאוחד כולל הכותרת והרשימה
st.markdown(f"""
<div class="unified-project-box">
    <h3>📁 פרויקטים ומרכיבים</h3>
    {project_list_html}
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 6. פגישות ותזכורות
col_right, col_left = st.columns(2)

with col_right:
    st.markdown("### 📅 פגישות היום")
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_m.iterrows():
            st.markdown(f"<div class='card'>📌 {row['meeting_title']}<br>🕒 {row['time']}<br>📁 {row['project_name']}</div>", unsafe_allow_html=True)

with col_left:
    st.markdown("### 🔔 תזכורות")
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    with st.container(height=260):
        if today_r.empty: st.info("אין תזכורות 🎉")
        else:
            for _, row in today_r.iterrows():
                icon = "🤖" if row["source"] == "ai" else "✍️"
                st.markdown(f"<div class='card'>{icon} {row['reminder_text']} | 📁 {row['project_name']}</div>", unsafe_allow_html=True)
    
    if st.button("➕ הוספת תזכורת"): st.session_state.add_mode = True
    if st.session_state.get("add_mode"):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1: text = st.text_input("תזכורת")
        with col2: proj = st.selectbox("פרויקט", projects["project_name"].tolist())
        with col3: 
            if st.button("✔"):
                new = {"reminder_text": text, "project_name": proj, "date": today, "source": "manual"}
                st.session_state.reminders_live.loc[len(st.session_state.reminders_live)] = new
                st.session_state.add_mode = False
                st.rerun()

# 7. AI האורקל
st.markdown("<div class='section-wrap' style='border-right: 6px solid #4facfe;'><h3>✨ סוכן ה-AI שלך</h3>", unsafe_allow_html=True)
api_key = st.secrets.get("GEMINI_API_KEY")
ca1, ca2 = st.columns([1, 2])
with ca1: sel_p = st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="p_sel")
with ca2: q_in = st.text_input("מה תרצי לדעת?", key="q_in")
if st.button("בצע ניתוח"):
    if q_in:
        with st.spinner("מנתח..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": f"Project: {sel_p}. Question: {q_in}"}]}]}, timeout=10)
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(f"<div class='card'>{ans}</div>", unsafe_allow_html=True)
            except: st.error("שגיאה בתקשורת")
st.markdown("</div>", unsafe_allow_html=True)
