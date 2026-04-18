import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. עיצוב CSS ---
st.set_page_config(layout="wide", page_title="Sivan Dashboard")

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7; direction: rtl; }
    
    /* העיצוב של המסגרת הגנרית */
    .card-start {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        text-align: right;
        direction: rtl;
    }

    .text-gradient {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .kpi-box {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e0e6ed;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    .list-item {
        background: #fdfdfd;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #eee;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* תיקון רכיבי Streamlit שיהיו RTL */
    div[data-testid="stMarkdownContainer"], .stSelectbox, .stTextInput, .stButton {
        text-align: right !important;
        direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. פונקציות עזר גנריות למסגרות ---
def open_card(title, icon=""):
    st.markdown(f'<div class="card-start"><h3>{icon} {title}</h3>', unsafe_allow_html=True)

def close_card():
    st.markdown('</div>', unsafe_allow_html=True)

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
st.markdown(f"<div style='text-align:center;'><h2 class='text-gradient'>Dashboard AI - ניהול פרויקטים</h2></div>", unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:120px; height:120px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 8px 16px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_b64}" style="width:100%; height:100%; object-fit: cover; object-position: center 15%;"></div></div>', unsafe_allow_html=True)
with p3:
    st.markdown(f'<div style="margin-top:20px;"><h3>{greeting}, סיון!</h3><p style="color:gray;">{now.strftime("%d/%m/%Y | %H:%M")}</p></div>', unsafe_allow_html=True)

# --- 5. שורת KPI ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-box' style='border-top:4px solid #ff4b4b;'>בסיכון 🔴<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-box' style='border-top:4px solid #ffa500;'>במעקב 🟡<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-box' style='border-top:4px solid #00c853;'>בתקין 🟢<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-box'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

# --- 6. הגוף המרכזי - פריסה בתוך המסגרות ---
col_right, col_left = st.columns([2, 1.2])

with col_right:
    # --- מלבן פרויקטים ---
    open_card("פרויקטים ומרכיבים", "📁")
    for _, row in projects.iterrows():
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        st.markdown(f'<div class="list-item"><span>{dot}</span><div style="flex-grow:1;"><b>{row["project_name"]}</b> <small style="color:gray;">| {row["project_type"]}</small></div></div>', unsafe_allow_html=True)
    close_card()

    # --- מלבן AI Oracle ---
    open_card("AI Oracle", "✨")
    ai_c1, ai_c2, ai_c3 = st.columns([1, 1.5, 0.5])
    with ai_c1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
    with ai_c2: st.text_input("שאלה ל-AI", placeholder="שאל משהו...", label_visibility="collapsed", key="ai_q")
    with ai_c3: 
        if st.button("🚀", key="ai_go"): st.info("מנתח...")
    close_card()

with col_left:
    # --- מלבן פגישות ---
    open_card("פגישות היום", "📅")
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if today_m.empty: st.write("אין פגישות להיום")
    else:
        for _, r in today_m.iterrows():
            st.markdown(f'<div class="list-item">📌 <b>{r["meeting_title"]}</b></div>', unsafe_allow_html=True)
    close_card()

    # --- מלבן תזכורות ---
    open_card("תזכורות", "🔔")
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    
    # אזור גלילה פנימי
    st.markdown('<div style="max-height:180px; overflow-y:auto; margin-bottom:10px;">', unsafe_allow_html=True)
    for _, row in today_r.iterrows():
        st.markdown(f'<div class="list-item">🔔 <div style="flex-grow:1;"><b>{row["reminder_text"]}</b><br><small style="color:#4facfe;">{row["project_name"]}</small></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ הוסף תזכורת"): st.session_state.show_add = True
    if st.session_state.get("show_add"):
        r_col1, r_col2 = st.columns([2, 1])
        with r_col1: nt = st.text_input("מה נזכור?", key="nt", label_visibility="collapsed")
        with r_col2: np = st.selectbox("לאיזה פרויקט?", projects["project_name"].tolist(), key="np", label_visibility="collapsed")
        if st.button("✅ שמור"):
            if nt:
                new_row = {"reminder_text": nt, "project_name": np, "date": today}
                st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.show_add = False
                st.rerun()
    close_card()
