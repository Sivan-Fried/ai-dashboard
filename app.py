import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות וטעינת נתונים ---
st.set_page_config(layout="wide", page_title="Dashboard")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("וודאי שקובצי האקסל קיימים"); st.stop()

# --- 2. הזרקת CSS גלובלי (רק לרקע ויישור כללי) ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7; direction: rtl; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .text-gradient {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.5rem; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. פונקציה גנרית ליצירת מלבן מעוצב (HTML טהור) ---
def render_styled_card(title, content_html, icon=""):
    card_html = f"""
    <div style="
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box;
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        direction: rtl;
        text-align: right;
        font-family: sans-serif;
    ">
        <h3 style="margin-top:0; color:#1f2a44;">{icon} {title}</h3>
        <div style="color: #444;">{content_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- 4. Header & Profile ---
st.markdown('<h1 class="text-gradient">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

col_p1, col_p2 = st.columns([1, 3])
with col_p1:
    if img_b64:
        st.markdown(f'<img src="data:image/png;base64,{img_b64}" style="width:120px; height:120px; border-radius:50%; border:4px solid white; box-shadow:0 8px 16px rgba(0,0,0,0.1); object-fit: cover;">', unsafe_allow_html=True)
with col_p2:
    st.markdown(f"<div style='margin-top:20px;'><h3>{greeting}, סיון!</h3><p>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. KPI Row ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
kpi_style = "background:white; padding:15px; border-radius:12px; text-align:center; border:1px solid #eee; box-shadow:0 2px 4px rgba(0,0,0,0.02);"
with k1: st.markdown(f"<div style='{kpi_style} border-top:4px solid red;'>בסיכון<br><b>{len(projects[projects['status']=='אדום'])}</b></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div style='{kpi_style} border-top:4px solid orange;'>במעקב<br><b>{len(projects[projects['status']=='צהוב'])}</b></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div style='{kpi_style} border-top:4px solid green;'>בתקין<br><b>{len(projects[projects['status']=='ירוק'])}</b></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div style='{kpi_style}'>סה\"כ פרויקטים<br><b>{len(projects)}</b></div>", unsafe_allow_html=True)

# --- 6. Main Content ---
col_main, col_side = st.columns([2, 1.2])

with col_main:
    # מלבן פרויקטים
    proj_html = "".join([f'<div style="background:#f9f9f9; padding:10px; margin-bottom:8px; border-radius:8px; border-right:5px solid {"green" if r["status"]=="ירוק" else "orange" if r["status"]=="צהוב" else "red"};"><b>{r["project_name"]}</b> | {r["project_type"]}</div>' for _, r in projects.iterrows()])
    render_styled_card("פרויקטים ומרכיבים", proj_html, "📁")

    # מלבן AI Oracle (כאן משלבים רכיב Streamlit בתוך מכולה מעוצבת)
    st.markdown('<div style="background: linear-gradient(white, white) padding-box, linear-gradient(90deg, #4facfe, #00f2fe) border-box; border: 2px solid transparent; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    st.markdown("### ✨ AI Oracle")
    ai_col1, ai_col2 = st.columns([1, 2])
    with ai_col1: st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed")
    with ai_col2: st.text_input("שאלה", placeholder="שאל את ה-AI...", label_visibility="collapsed")
    st.button("שגר שאילתה 🚀")
    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    # מלבן פגישות
    meet_html = "".join([f'<div style="background:#f9f9f9; padding:10px; margin-bottom:8px; border-radius:8px;">📌 {r["meeting_title"]}</div>' for _, r in meetings.iterrows()]) if not meetings.empty else "אין פגישות היום"
    render_styled_card("פגישות היום", meet_html, "📅")

    # מלבן תזכורות
    rem_html = "".join([f'<div style="background:#f9f9f9; padding:10px; margin-bottom:8px; border-radius:8px;">🔔 {r["reminder_text"]}</div>' for _, r in reminders.iterrows()])
    render_styled_card("תזכורות", rem_html, "🔔")
    if st.button("➕ הוסף תזכורת"):
        st.info("כאן תבוא הלוגיקה להוספה")
