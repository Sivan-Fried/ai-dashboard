import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות ועיצוב (Style Engine) ---
st.set_page_config(layout="wide", page_title="ניהול פרויקטים גנרי")

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7; direction: rtl; }
    
    /* הגדרת המלבן הגנרי - יוחל על כל מה שיוכנס ל-Container עם הגדרה זו */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }

    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .list-item {
        background: #fdfdfd;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 12px;
        text-align: right;
    }

    /* יישור גנרי לכל רכיבי המערכת */
    .stSelectbox, .stTextInput, .stButton, label, h3, p, .stMarkdown {
        direction: rtl !important;
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. פונקציות עזר גנריות ---

def create_card(title, icon=""):
    """מייצרת מכולה מעוצבת עם כותרת"""
    container = st.container(border=True)
    container.markdown(f"### {icon} {title}")
    return container

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל קיימים"); st.stop()

if "reminders_live" not in st.session_state: 
    st.session_state.reminders_live = reminders.copy()

# --- 4. Header & Profile ---
st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><h2 style='font-weight:800;'><span class='text-gradient'>Dashboard AI</span></h2></div>", unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

col_p1, col_p2, col_p3 = st.columns([1, 1, 2])
with col_p2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:130px; height:130px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 20%;"></div></div>', unsafe_allow_html=True)
with col_p3:
    st.markdown(f'<div style="margin-top:25px;"><h3>{greeting}, סיון!</h3><p style="color:gray;">{now.strftime("%d/%m/%Y | %H:%M")}</p></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)

# --- 5. Main Dashboard Layout ---
col_main, col_side = st.columns([2, 1.2])

with col_main:
    # שימוש בפונקציה הגנרית ליצירת מלבן פרויקטים
    with create_card("פרויקטים ומרכיבים", "📁"):
        for _, row in projects.iterrows():
            dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
            st.markdown(f'<div class="list-item"><span>{dot}</span><div style="flex-grow:1;"><b>{row["project_name"]}</b> <small style="color:gray;">| {row["project_type"]}</small></div></div>', unsafe_allow_html=True)

    # שימוש בפונקציה הגנרית ליצירת מלבן AI
    with create_card("AI Oracle", "✨"):
        ca1, ca2, ca3 = st.columns([1, 1.5, 0.5])
        with ca1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with ca2: st.text_input("שאלה", placeholder="שאל את ה-AI...", label_visibility="collapsed", key="ai_q")
        with ca3: 
            if st.button("🚀", key="ai_go"): st.info("מנתח...")

with col_side:
    # שימוש בפונקציה הגנרית ליצירת מלבן פגישות
    with create_card("פגישות היום", "📅"):
        today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if today_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in today_m.iterrows():
                st.markdown(f'<div class="list-item">📌 <b>{r["meeting_title"]}</b></div>', unsafe_allow_html=True)

    # שימוש בפונקציה הגנרית ליצירת מלבן תזכורות
    with create_card("תזכורות", "🔔"):
        today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
        
        with st.container(height=200, border=False):
            for _, row in today_r.iterrows():
                st.markdown(f'<div class="list-item">🔔 <div style="flex-grow:1;"><b>{row["reminder_text"]}</b><br><small style="color:#4facfe;">{row["project_name"]}</small></div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("➕ הוסף תזכורת"): st.session_state.show_add = True
        
        if st.session_state.get("show_add"):
            ra, rb, rc = st.columns([1.5, 1, 0.6])
            with ra: nt = st.text_input("תזכורת", key="nt", label_visibility="collapsed")
            with rb: np = st.selectbox("פרויקט", projects["project_name"].tolist(), key="np", label_visibility="collapsed")
            with rc: 
                if st.button("✅"):
                    if nt:
                        new_r = {"reminder_text": nt, "project_name": np, "date": today}
                        st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_r])], ignore_index=True)
                        st.session_state.show_add = False
                        st.rerun()
