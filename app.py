import streamlit as st
import pandas as pd
import base64
import datetime
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS גלובלי ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .profile-img {
        width: 130px; height: 130px; border-radius: 50% !important;
        object-fit: cover !important; object-position: center 25% !important;
        border: 4px solid white !important; box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    /* KPI - רקע לבן, בלי מסגרת תכלת, עובי דק */
    .kpi-card {
        background: white !important;
        padding: 10px !important;
        border-radius: 12px !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        border: none !important; /* הסרת המסגרת לחלוטין */
    }

    /* מסגרות הקונטיינרים */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(90deg, #4facfe, #00f2fe) border-box !important;
        border: 1.5px solid transparent !important;
        border-radius: 18px !important;
        padding: 15px !important;
        background-color: white !important;
    }

    h3, p, span, label, .stSelectbox, .stTextInput { text-align: right !important; direction: rtl !important; }
</style>
""", unsafe_allow_html=True)

# פונקציה ליצירת רשימה נגללת בתוך HTML כדי להבטיח גלילה
def render_scrollable_list(df, type_tag="blue", is_reminder=False):
    rows_html = ""
    for _, row in df.iterrows():
        label = row.get('project_name', 'כללי')
        text = row['reminder_text'] if is_reminder else row['project_name']
        tag_class = "tag-orange" if is_reminder else "tag-blue"
        icon = "🔔" if is_reminder else "📂"
        
        rows_html += f"""
        <div style="background:white; padding:10px 15px; border-radius:10px; margin-bottom:8px; 
                    border:1px solid #edf2f7; border-right:5px solid #4facfe; display:flex; 
                    justify-content:space-between; align-items:center; direction:rtl; font-family:sans-serif;">
            <span style="font-size:0.95rem; color:#1f2a44;">{icon} {text}</span>
            <span style="color:{'#d97706' if is_reminder else '#4facfe'}; font-size:0.8em; font-weight:600; 
                        background:{'#fffbeb' if is_reminder else '#f0f9ff'}; padding:2px 8px; border-radius:5px;">
                {label if is_reminder else row.get('project_type', 'פרויקט')}
            </span>
        </div>
        """
    
    full_html = f"""
    <div style="max-height:300px; overflow-y:auto; padding:5px; direction:rtl;">
        {rows_html}
    </div>
    """
    return st.components.v1.html(full_html, height=310, scrolling=False)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()
if "show_add" not in st.session_state: st.session_state.show_add = False

# --- 4. תצוגה עליונה ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1, 1, 2])
with p2:
    if img_b64:
        st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/png;base64,{img_b64}" class="profile-img"></div>', unsafe_allow_html=True)
with p3:
    st.markdown(f"<div><h3>{greeting}, סיון!</h3><p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p></div>", unsafe_allow_html=True)

# --- 5. שורת KPI - רקע לבן, בלי בורדר תכלת ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

# --- 6. גוף הדשבורד ---
st.markdown("<br>", unsafe_allow_html=True)
col_right, col_left = st.columns([2, 1.2])

with col_right:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים ומרכיבים")
        render_scrollable_list(projects)

    with st.container(border=True):
        st.markdown("### ✨ AI Oracle")
        a1, a2 = st.columns([1, 2])
        with a1: st.selectbox("בחר פרויקט", projects["project_name"].tolist(), label_visibility="collapsed", key="ai_p")
        with a2: st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed", key="ai_i")
        st.button("שגר שאילתה 🚀", key="ai_btn", use_container_width=True)

with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות היום")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div style="background:white; padding:10px; border-radius:10px; border-right:5px solid #4facfe; margin-bottom:5px;">📌 {r["meeting_title"]}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        render_scrollable_list(t_r, is_reminder=True)
        
        if not st.session_state.show_add:
            if st.button("➕ הוסף תזכורת", key="add_btn"):
                st.session_state.show_add = True
                st.rerun()
        else:
            st.markdown("---")
            nt = st.text_input("משימה", key="new_t")
            np = st.selectbox("פרויקט", projects["project_name"].tolist(), key="new_p")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ שמור"):
                    if nt:
                        new_r = pd.DataFrame([{"reminder_text": nt, "date": today, "project_name": np}])
                        st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_r], ignore_index=True)
                        st.session_state.show_add = False
                        st.rerun()
            with c2:
                if st.button("ביטול"):
                    st.session_state.show_add = False
                    st.rerun()
