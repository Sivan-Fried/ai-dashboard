import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ורקע ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# הזרקת RTL בסיסי
st.markdown("<style>.stApp { direction: rtl; background-color: #f2f4f7; }</style>", unsafe_allow_html=True)

# --- 2. פונקציית הקסם למסגרת מעוצבת חסינה ---
def create_card(title, icon, content_html):
    card_html = f"""
    <div style="
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        text-align: right;
        direction: rtl;
        font-family: sans-serif;
    ">
        <h3 style="margin-top:0; color:#1f2a44; border-bottom: 1px solid #eee; padding-bottom: 10px;">{icon} {title}</h3>
        <div style="margin-top: 15px;">{content_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("קובצי האקסל חסרים"); st.stop()

# --- 4. כותרת ראשית (גרדיאנט מקובע) ---
st.markdown("""
    <h1 style="
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 30px;
    ">Dashboard AI</h1>
""", unsafe_allow_html=True)

# --- 5. פרופיל וברכה ---
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
    st.markdown(f"<div style='margin-top:25px; text-align:right;'><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 6. KPI Row ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k_temp = "<div style='background:white; padding:15px; border-radius:12px; text-align:center; border-top:4px solid {color}; box-shadow:0 2px 5px rgba(0,0,0,0.02);'><b>{label}</b><br><span style='font-size:22px;'>{val}</span></div>"
with k1: st.markdown(k_temp.format(color="#ff4b4b", label="בסיכון 🔴", val=len(projects[projects['status']=='אדום'])), unsafe_allow_html=True)
with k2: st.markdown(k_temp.format(color="#ffa500", label="במעקב 🟡", val=len(projects[projects['status']=='צהוב'])), unsafe_allow_html=True)
with k3: st.markdown(k_temp.format(color="#00c853", label="בתקין 🟢", val=len(projects[projects['status']=='ירוק'])), unsafe_allow_html=True)
with k4: st.markdown(k_temp.format(color="#4facfe", label="סה\"כ פרויקטים", val=len(projects)), unsafe_allow_html=True)

# --- 7. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
right_col, left_col = st.columns([2, 1.2])

with right_col:
    # פרויקטים
    proj_html = "".join([f'<div style="background:#fdfdfd; padding:10px; margin-bottom:8px; border-radius:8px; border-right:4px solid #4facfe;">{row["project_name"]}</div>' for _, row in projects.iterrows()])
    create_card("פרויקטים ומרכיבים", "📁", proj_html)

    # AI Oracle (שימוש ב-container מעוצב ספציפית)
    st.markdown("""
        <div style="background: linear-gradient(white, white) padding-box, linear-gradient(90deg, #4facfe, #00f2fe) border-box; border: 2px solid transparent; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); direction: rtl; text-align: right;">
            <h3 style="margin-top:0; color:#1f2a44;">✨ AI Oracle</h3>
    """, unsafe_allow_html=True)
    a1, a2 = st.columns([1, 2])
    with a1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
    with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_q")
    st.button("שגר שאילתה 🚀", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with left_col:
    # פגישות
    meet_today = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    meet_html = "".join([f'<div style="background:#fdfdfd; padding:10px; margin-bottom:8px; border-radius:8px;">📌 {r["meeting_title"]}</div>' for _, r in meet_today.iterrows()]) if not meet_today.empty else "אין פגישות היום"
    create_card("פגישות היום", "📅", meet_html)

    # תזכורות
    rem_today = reminders[pd.to_datetime(reminders["date"]).dt.date == today]
    rem_html = "".join([f'<div style="background:#fdfdfd; padding:10px; margin-bottom:8px; border-radius:8px;">🔔 {r["reminder_text"]}</div>' for _, r in rem_today.iterrows()])
    create_card("תזכורות", "🔔", rem_html)
    st.button("➕ הוסף תזכורת")
