import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרות עמוד ועיצוב CSS
st.set_page_config(layout="wide", page_title="ניהול פרויקטים - לוח בקרה")

st.markdown("""
<style>
    body, .stApp { background-color: #f2f4f7; direction: rtl; }
    
    .text-gradient {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* המלבן המעוצב - עיצוב אחיד לכל המכולות */
    .fancy-container, div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        direction: rtl;
    }

    .list-item {
        background: #fdfdfd;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .kpi-card {
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e0e6ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        height: 85px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* תיקון יישור לרכיבי Streamlit */
    .stSelectbox, .stTextInput, .stButton {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# 2. נתונים ופונקציות
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

img_base64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל קיימים"); st.stop()

if "reminders_live" not in st.session_state: 
    st.session_state.reminders_live = reminders.copy()

# 3. כותרת עליונה
st.markdown("<div style='text-align:center; margin-bottom:20px;'><h2 style='font-weight:800;'><span class='text-gradient'>Dashboard AI</span> <span style='color: #1f2a44;'>ניהול פרויקטים</span></h2></div>", unsafe_allow_html=True)

col_head1, col_head2 = st.columns([1, 3])
with col_head1:
    if img_base64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><div style="width:110px; height:110px; border-radius:50%; overflow:hidden; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);"><img src="data:image/png;base64,{img_base64}" style="width:100%; height:100%; object-fit: cover;"></div></div>', unsafe_allow_html=True)
with col_head2:
    st.markdown(f'<div style="margin-top:20px;"><h3>{greeting}, סיון!</h3><p style="color:gray;">{now.strftime("%d/%m/%Y | %H:%M")}</p></div>', unsafe_allow_html=True)

# 4. KPI
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card' style='border-top:3px solid red;'><p style='color:gray; margin:0;'>בסיכון 🔴</p><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card' style='border-top:3px solid orange;'><p style='color:gray; margin:0;'>במעקב 🟡</p><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card' style='border-top:3px solid green;'><p style='color:gray; margin:0;'>בתקין 🟢</p><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><p style='color:gray; margin:0;'>סה\"כ פרויקטים</p><b>{len(projects)}</b></div>", unsafe_allow_html=True)

st.markdown("---")

# 5. גוף הדשבורד
col_main, col_side = st.columns([2, 1])

with col_main:
    # מלבן פרויקטים
    project_items_html = ""
    icons_map = {"פרויקט אקטיבי": "🚀", "חבילת עבודה": "📦", "תחזוקה": "🔧"}
    for _, row in projects.iterrows():
        icon = icons_map.get(row['project_type'], "📁")
        dot = "🟢" if row["status"]=="ירוק" else "🟡" if row["status"]=="צהוב" else "🔴"
        project_items_html += f'<div class="list-item"><span>{dot}</span><div style="flex-grow:1;"><b>{icon} {row["project_name"]}</b> <span style="color:gray; font-size:12px; margin-right:5px;">| {row["project_type"]}</span></div></div>'
    
    st.markdown(f'<div class="fancy-container"><h3 style="margin-top:0;">📁 פרויקטים ומרכיבים</h3>{project_items_html}</div>', unsafe_allow_html=True)

    # מלבן AI Oracle (מעוצב דרך ה-CSS של st.container)
    with st.container(border=True):
        st.markdown('<h3 style="margin-top:0;">✨ AI Oracle</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px; color:gray;">ניתוח חכם של נתוני הפרויקטים</p>', unsafe_allow_html=True)
        c_ai1, c_ai2, c_ai3 = st.columns([1, 1.5, 0.5])
        with c_ai1: 
            st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with c_ai2: 
            st.text_input("שאלה", placeholder="מה סטטוס הפרויקט?", label_visibility="collapsed", key="ai_q")
        with c_ai3: 
            if st.button("🚀", use_container_width=True): st.info("מנתח...")

with col_side:
    # מלבן פגישות
    today_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    meet_html = ""
    if today_m.empty: meet_html = "<p style='color:gray;'>אין פגישות להיום</p>"
    else:
        for _, row in today_m.iterrows():
            meet_html += f'<div class="list-item">📌 <div><b>{row["meeting_title"]}</b><br><small>{row["time"]}</small></div></div>'
    st.markdown(f'<div class="fancy-container"><h3 style="margin-top:0;">📅 פגישות היום</h3>{meet_html}</div>', unsafe_allow_html=True)

    # מלבן תזכורות (משולב HTML ורכיבי הוספה)
    st.markdown('<div class="fancy-container"><h3 style="margin-top:0;">🔔 תזכורות</h3>', unsafe_allow_html=True)
    
    today_r = st.session_state.reminders_live[pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today]
    if today_r.empty:
        st.markdown("<p style='color:gray;'>אין תזכורות להיום</p>", unsafe_allow_html=True)
    else:
        for _, row in today_r.iterrows():
            st.markdown(f"""
            <div class="list-item">
                🔔 <div style="flex-grow:1;">
                    <b>{row['reminder_text']}</b><br>
                    <small style="color:#4facfe;">שיוך: {row['project_name']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # הוספה מהירה בתחתית המלבן
    if st.button("➕ תזכורת חדשה", key="add_btn"):
        st.session_state.show_add = True
    
    if st.session_state.get("show_add"):
        c1, c2, c3 = st.columns([1.5, 1, 0.6])
        with c1: nt = st.text_input("מה להזכיר?", label_visibility="collapsed", key="nt")
        with c2: np = st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="np")
        with c3: 
            if st.button("✅"):
                if nt:
                    new_row = {"reminder_text": nt, "project_name": np, "date": today}
                    st.session_state.reminders_live = pd.concat([st.session_state.reminders_live, pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state.show_add = False
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
