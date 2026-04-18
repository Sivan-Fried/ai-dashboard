import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הזרקת CSS סופי ומוחלט (מתלבש על המכולות של Streamlit) ---
st.set_page_config(layout="wide", page_title="Dashboard")

st.markdown("""
<style>
    /* רקע כללי */
    .stApp { background-color: #f2f4f7; direction: rtl; }
    
    /* העיצוב של המסגרות - תופס כל container עם border=True */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        padding: 22px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06) !important;
        margin-bottom: 25px !important;
    }

    /* יישור לימין לכל התוכן */
    div[data-testid="stVerticalBlock"] { direction: rtl !important; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .kpi-card {
        background: white; padding: 15px; border-radius: 12px;
        text-align: center; border: 1px solid #e0e6ed;
    }

    .list-item {
        background: #fdfdfd; padding: 12px; border-radius: 10px;
        margin-bottom: 10px; border: 1px solid #eee;
        display: flex; align-items: center; gap: 12px;
    }

    /* תיקון יישור לשדות טקסט וכפתורים */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton, label {
        text-align: right !important; direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. פונקציות עזר ---
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

def styled_container(title, icon=""):
    """יוצר מכולה מעוצבת שכל מה שבתוכה נשאר בתוכה"""
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        return st.container()

# --- 3. נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל קיימים"); st.stop()

if "reminders_live" not in st.session_state: 
    st.session_state.reminders_live = reminders.copy()

# --- 4. Header ---
st.markdown(f"<div style='text-align:center;'><h2 class='text-gradient'>Dashboard AI</h2></div>", unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

h1, h2, h3 = st.columns([1, 1, 2])
with h2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" style="width:120px; height:120px; border-radius:50%; border:4px solid white; box-shadow:0 8px 16px rgba(0,0,0,0.1); object-fit: cover;"></div>', unsafe_allow_html=True)
with h3:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI Section ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:4px solid red;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:4px solid orange;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:4px solid green;'>בתקין 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 6. הגוף המרכזי ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # מלבן פרויקטים
    with styled_container("פרויקטים ומרכיבים", "📁"):
        for _, row in projects.iterrows():
            dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
            st.markdown(f'<div class="list-item"><span>{dot}</span><b>{row["project_name"]}</b> <small style="color:gray; margin-right:auto;">{row["project_type"]}</small></div>', unsafe_allow_html=True)

    # מלבן AI Oracle - עכשיו הכל בפנים
    with styled_container("AI Oracle", "✨"):
        ai_1, ai_2 = st.columns([1, 2])
        with ai_1: st.selectbox("פרויקט", projects["project_name"].tolist(), key="ai_proj", label_visibility="collapsed")
        with ai_2: st.text_input("שאלה", placeholder="שאל את ה-AI...", key="ai_ques", label_visibility="collapsed")
        if st.button("שגר שאילתה 🚀", use_container_width=True):
            st.info("מנתח נתונים...")

with col_left:
    # פגישות היום
    with styled_container("פגישות היום", "📅"):
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות להיום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="list-item">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    # תזכורות
    with styled_container("תזכורות", "🔔"):
        today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
        with st.container(height=180, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f'<div class="list-item">🔔 {row["reminder_text"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("➕ הוסף תזכורת"): st.session_state.add_mode = True
        if st.session_state.get("add_mode"):
            nt = st.text_input("מה נזכור?", key="new_task")
            if st.button("✅ שמור"):
                new_row = {"reminder_text": nt, "date": today}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.add_mode = False
                st.rerun()
