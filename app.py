import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS "בטון"
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - סיוון")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #f2f4f7;
    }

    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* עיצוב המכולה של הפרויקטים */
    .section-wrap {
        background: white;
        border: 2px solid #4facfe;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* כרטיסי KPI */
    .kpi-box {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    /* תמונת פרופיל מושלמת */
    .profile-img {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        object-fit: cover;
        object-position: center;
        border: 4px solid white;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    /* יישור טפסים וכפתורים */
    .stButton>button { width: 100%; border-radius: 8px; }
    div[data-testid="stForm"] { direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# 2. חלק עליון: כותרת, תמונה וברכה
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

# כותרת דאשבורד
st.markdown(f"<div style='text-align:center;'><h1 class='text-gradient'>לוח בקרה חכם</h1></div>", unsafe_allow_html=True)

# שורת פרופיל
col_spacer1, col_info, col_img, col_spacer2 = st.columns([1, 2, 1, 1])

with col_info:
    st.markdown(f"""
    <div style="margin-top: 30px;">
        <h2 style="margin:0; color:#1f2a44;">{greeting}, סיון!</h2>
        <p style="color:gray; font-size:18px;">{now.strftime("%d/%m/%Y | %H:%M")}</p>
    </div>
    """, unsafe_allow_html=True)

with col_img:
    if img_base64:
        st.markdown(f'<img src="data:image/png;base64,{img_base64}" class="profile-img">', unsafe_allow_html=True)

st.markdown("---")

# 3. נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל והתמונה נמצאים בתיקייה"); st.stop()

if "reminders_live" not in st.session_state:
    st.session_state.reminders_live = reminders.copy()

# 4. KPI - חלק עליון
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-box'><p>סה״כ פרויקטים</p><h3>{len(projects)}</h3></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-box' style='border-top: 4px solid #ff4b4b;'><p>בסיכון 🔴</p><h3 style='color:#ff4b4b;'>{len(projects[projects['status']=='אדום'])}</h3></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-box' style='border-top: 4px solid #ffa500;'><p>במעקב 🟡</p><h3 style='color:#ffa500;'>{len(projects[projects['status']=='צהוב'])}</h3></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-box' style='border-top: 4px solid #00c853;'><p>בתקין 🟢</p><h3 style='color:#00c853;'>{len(projects[projects['status']=='ירוק'])}</h3></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. פרויקטים - המלבן המאוחד (רק לכותרת)
with st.container():
    st.markdown("""<div style='background:white; border:1px solid #ddd; padding:15px; border-radius:12px; margin-bottom:15px;'>
        <h3 style='margin:0;'>📁 פרויקטים ומרכיבים</h3>
    </div>""", unsafe_allow_html=True)
    
    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        st.markdown(f"""<div style='background:white; padding:12px; border-radius:10px; border:1px solid #eee; margin-bottom:8px; display:flex; justify-content:space-between;'>
            <span>{dot}</span>
            <b>{row['project_name']}</b>
        </div>""", unsafe_allow_html=True)

# 6. לו"ז ותזכורות
col_r, col_l = st.columns(2)

with col_r:
    st.subheader("📅 פגישות היום")
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.info("אין פגישות היום")
    else:
        for _, row in today_m.iterrows():
            st.info(f"📌 {row['meeting_title']} | {row['time']}")

with col_l:
    st.subheader("🔔 תזכורות")
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    with st.container(height=250):
        for _, row in today_r.iterrows():
            st.success(f"🔔 {row['reminder_text']}")
    
    # הוספת תזכורת
    with st.expander("➕ הוסף תזכורת חדשה"):
        with st.form("add_reminder"):
            new_txt = st.text_input("מה התזכורת?")
            new_proj = st.selectbox("פרויקט", projects["project_name"].tolist())
            if st.form_submit_button("שמור"):
                new_data = {"reminder_text": new_txt, "project_name": new_proj, "date": today, "source": "manual"}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_data])], ignore_index=True)
                st.rerun()

# 7. AI Oracle
st.markdown("---")
st.markdown("### ✨ AI Oracle")
c1, c2 = st.columns([1, 2])
with c1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), key="ai_p")
with c2: st.text_input("שאלה לבוט", key="ai_q")
if st.button("נתח נתונים"):
    st.info("מנתח את נתוני הפרויקט...")
