import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות בסיסיות ויישור RTL ---
st.set_page_config(layout="wide", page_title="Dashboard AI")

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7; direction: rtl; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    div[data-testid="stVerticalBlock"] { direction: rtl; }
    
    /* כותרת גרדיאנט חסינה */
    .title-gradient {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem; font-weight: 900; text-align: center;
        margin-bottom: 30px; font-family: sans-serif;
    }
</style>
""", unsafe_allow_html=True)

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. פונקציית כרטיס חסינת עיצוב ---
def styled_card_start(title, icon=""):
    st.markdown(f"""
        <div style="
            background: linear-gradient(white, white) padding-box,
                        linear-gradient(90deg, #4facfe, #00f2fe) border-box;
            border: 2px solid transparent;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            text-align: right;
            direction: rtl;
        ">
            <h3 style="margin-top:0; color:#1f2a44;">{icon} {title}</h3>
        </div>
    """, unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("קובצי הנתונים לא נמצאו"); st.stop()

# --- 4. Header & Profile ---
st.markdown('<h1 class="title-gradient">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64:
        st.markdown(f'''
            <div style="display:flex; justify-content:center;">
                <div style="width:140px; height:140px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;">
                </div>
            </div>''', unsafe_allow_html=True)
with p3:
    st.markdown(f"<div style='margin-top:25px;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI Row ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k_style = "background:white; padding:15px; border-radius:12px; text-align:center; border:1px solid #eef; box-shadow:0 2px 4px rgba(0,0,0,0.02);"
with k1: st.markdown(f"<div style='{k_style} border-top:4px solid #ff4b4b;'>בסיכון<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div style='{k_style} border-top:4px solid #ffa500;'>במעקב<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div style='{k_style} border-top:4px solid #00c853;'>בתקין<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div style='{k_style}'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 6. הגוף המרכזי ---
st.markdown("<br>", unsafe_allow_html=True)
col_r, col_l = st.columns([2, 1.2])

with col_r:
    # כרטיס פרויקטים
    styled_card_start("פרויקטים ומרכיבים", "📁")
    for _, row in projects.iterrows():
        st.markdown(f'<div style="background:white; padding:10px; margin-bottom:5px; border-radius:8px; border-right:4px solid #4facfe;">{row["project_name"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # כרטיס AI Oracle - כאן הזרקנו את העיצוב סביב הרכיבים
    st.markdown("""<div style="background: linear-gradient(white, white) padding-box, linear-gradient(90deg, #4facfe, #00f2fe) border-box; border: 2px solid transparent; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: right; direction: rtl;">
                <h3 style="margin-top:0; color:#1f2a44;">✨ AI Oracle</h3>""", unsafe_allow_html=True)
    a1, a2 = st.columns([1, 2])
    with a1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
    with a2: st.text_input("שאלה", placeholder="שאלי משהו...", label_visibility="collapsed", key="ai_q")
    st.button("שגר שאילתה 🚀", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_l:
    # כרטיס פגישות
    styled_card_start("פגישות היום", "📅")
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.write("אין פגישות היום")
    else:
        for _, r in today_m.iterrows():
            st.markdown(f'<div style="background:white; padding:10px; margin-bottom:5px; border-radius:8px;">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # כרטיס תזכורות
    styled_card_start("תזכורות", "🔔")
    today_r = reminders[pd.to_datetime(reminders["date"]).dt.date == today]
    for _, row in today_r.iterrows():
        st.markdown(f'<div style="background:white; padding:10px; margin-bottom:5px; border-radius:8px;">🔔 {row["reminder_text"]}</div>', unsafe_allow_html=True)
    st.button("➕ הוסף תזכורת")
