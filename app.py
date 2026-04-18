import streamlit as st
import pandas as pd
import base64
import datetime
import time
from zoneinfo import ZoneInfo

# --- 1. הגדרות דף ---
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 2. CSS מלוטש - יישור ימין מלא, ניקיון עיצובי ופונט אחיד ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stApp { background-color: #f8fafc !important; }
    
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center !important;
        font-size: 2.5rem !important;
        font-weight: 800;
        margin-bottom: 25px;
    }

    /* פרופיל */
    .profile-container { display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 30px; }
    .profile-img {
        width: 120px; height: 120px; border-radius: 50%;
        object-fit: cover; object-position: center 25%;
        border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    }

    /* KPI - נקי, לבן, יישור ימין */
    .kpi-box {
        background: white; padding: 20px; border-radius: 15px;
        text-align: right; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: none; min-height: 100px;
    }
    .kpi-label { color: #64748b; font-size: 0.9rem; font-weight: 600; }
    .kpi-value { font-size: 1.8rem; font-weight: 800; color: #1e293b; display: block; }

    /* קונטיינרים עם מסגרת דקה */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-top: 4px solid #4facfe !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05) !important;
    }

    /* אלמנטים של רשימה */
    .list-item {
        background: #f8fafc; padding: 12px 15px; border-radius: 10px;
        margin-bottom: 10px; border-right: 5px solid #4facfe;
        display: flex; justify-content: space-between; align-items: center;
        direction: rtl;
    }
    .tag { font-size: 0.75rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; }
    .tag-p { background: #e0f2fe; color: #0369a1; }
    .tag-r { background: #fef3c7; color: #92400e; }

    /* תיקון פוקוס וכפתורים */
    .stButton>button { border-radius: 10px !important; font-weight: 700 !important; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 3. טעינת נתונים ---
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("שגיאה בטעינת הקבצים - וודאי שהם קיימים"); st.stop()

if "rem_live" not in st.session_state: st.session_state.rem_live = reminders.copy()
if "show_add" not in st.session_state: st.session_state.show_add = False
if "ai_msg" not in st.session_state: st.session_state.ai_msg = None

# --- 4. כותרת ופרופיל ---
st.markdown('<h1 class="dashboard-header">Sivan\'s Workspace</h1>', unsafe_allow_html=True)

img_b64 = get_base64_image("profile.png")
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

st.markdown(f"""
<div class="profile-container">
    <div style="text-align: right;">
        <h2 style="margin:0; font-weight:800; color:#1e293b;">{greeting}, סיון</h2>
        <p style="margin:0; color:#64748b;">{now.strftime('%d/%m/%Y | %H:%M')}</p>
    </div>
    <img src="data:image/png;base64,{img_b64}" class="profile-img">
</div>
""", unsafe_allow_html=True)

# --- 5. שורת KPI נקייה ---
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-box"><span class="kpi-label">בסיכון 🔴</span><span class="kpi-value">{len(projects[projects["status"]=="אדום"])}</span></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-box"><span class="kpi-label">במעקב 🟡</span><span class="kpi-value">{len(projects[projects["status"]=="צהוב"])}</span></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-box"><span class="kpi-label">תקין 🟢</span><span class="kpi-value">{len(projects[projects["status"]=="ירוק"])}</span></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-box"><span class="kpi-label">סה"כ פרויקטים</span><span class="kpi-value">{len(projects)}</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. גוף הדשבורד ---
col_right, col_left = st.columns([1.8, 1.2])

with col_right:
    with st.container():
        st.markdown("### 📁 פרויקטים ומרכיבים")
        # גלילה מובנית ב-HTML ליישור מקסימלי
        proj_html = "".join([f'<div class="list-item"><span>📂 {row["project_name"]}</span><span class="tag tag-p">{row.get("project_type", "פרויקט")}</span></div>' for _, row in projects.iterrows()])
        st.components.v1.html(f'<div style="direction:rtl; max-height:300px; overflow-y:auto; padding-left:10px;">{proj_html}</div>', height=310)

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### ✨ AI Oracle")
        c1, c2 = st.columns([1, 2])
        with c1: p_sel = st.selectbox("פרויקט", projects["project_name"].tolist(), label_visibility="collapsed")
        with c2: q_in = st.text_input("שאלה", placeholder="מה תרצי לדעת?", label_visibility="collapsed")
        
        if st.button("נתח נתונים 🚀", use_container_width=True):
            if q_in:
                with st.spinner("מעבד..."):
                    time.sleep(1)
                    st.session_state.ai_msg = f"**ניתוח AI עבור {p_sel}:** הנתונים מראים יציבות. מומלץ לוודא עמידה ביעדי סוף החודש."
            else: st.warning("נא להזין שאלה")
        
        if st.session_state.ai_msg:
            st.info(st.session_state.ai_msg)

with col_left:
    with st.container():
        st.markdown("### 📅 פגישות היום")
        t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
        if t_m.empty: st.write("אין פגישות מתוזמנות")
        else:
            for _, r in t_m.iterrows():
                st.markdown(f'<div class="list-item"><span>📌 {r["meeting_title"]}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown("### 🔔 תזכורות")
        t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
        rem_html = "".join([f'<div class="list-item"><span>🔔 {row["reminder_text"]}</span><span class="tag tag-r">{row.get("project_name", "כללי")}</span></div>' for _, row in t_r.iterrows()])
        st.components.v1.html(f'<div style="direction:rtl; max-height:250px; overflow-y:auto; padding-left:10px;">{rem_html}</div>', height=260)
        
        if not st.session_state.show_add:
            if st.button("➕ הוסף תזכורת", use_container_width=True):
                st.session_state.show_add = True
                st.rerun()
        else:
            with st.form("add_rem", clear_on_submit=True):
                nt = st.text_input("מה המשימה?")
                np = st.selectbox("שיוך לפרויקט", projects["project_name"].tolist())
                c1, c2 = st.columns(2)
                with c1: 
                    if st.form_submit_button("✅ שמור"):
                        if nt:
                            new_r = pd.DataFrame([{"reminder_text": nt, "date": today, "project_name": np}])
                            st.session_state.rem_live = pd.concat([st.session_state.rem_live, new_r], ignore_index=True)
                            st.session_state.show_add = False
                            st.rerun()
                with c2:
                    if st.form_submit_button("ביטול"):
                        st.session_state.show_add = False
                        st.rerun()
