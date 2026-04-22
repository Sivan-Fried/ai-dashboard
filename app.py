import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components
import google.generativeai as genai
from streamlit_js_eval import get_geolocation

# =========================================================
# 1. הגדרות דף ותשתית נתונים
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

# פונקציות לניהול סיכומים קבועים
def load_saved_summaries():
    try:
        return pd.read_excel("fathom_summaries.xlsx")
    except:
        return pd.DataFrame(columns=["recording_id", "summary", "date"])

def save_summary_to_file(rec_id, summary_text):
    df = load_saved_summaries()
    rec_id = str(rec_id)
    if rec_id not in df['recording_id'].astype(str).values:
        new_row = pd.DataFrame([{
            "recording_id": rec_id,
            "summary": summary_text,
            "date": datetime.datetime.now().strftime("%d/%m/%Y")
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel("fathom_summaries.xlsx", index=False)

# שליפת מיקום ומזג אוויר
def get_weather_data(lat=32.084, lon=34.887): # ברירת מחדל פתח תקווה
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            return f"{temp}°C | {desc}"
    except: pass
    return "פתח תקווה | 24°C"

loc = get_geolocation()
if loc and 'coords' in loc:
    weather_info = get_weather_data(loc['coords']['latitude'], loc['coords']['longitude'])
else:
    weather_info = get_weather_data()

# =========================================================
# 2. עיצוב (CSS)
# =========================================================
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    .stInfo, [data-testid="stNotification"], .stMarkdown div {
        text-align: right !important;
        direction: rtl !important;
    }
    .stInfo ul, .stInfo ol {
        direction: rtl !important;
        text-align: right !important;
        padding-right: 1.8rem !important;
        padding-left: 0 !important;
    }

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
    
    .record-row {
        background: #ffffff !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 3px !important;
        border: 1px solid #edf2f7 !important;
        border-right: 5px solid #4facfe !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        direction: rtl !important;
    }

    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    h3 { text-align: right !important; color: #1f2a44 !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. פונקציות API
# =========================================================

def get_fathom_meetings():
    url = "https://api.fathom.ai/external/v1/meetings"
    headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get('items', [])[:5], res.status_code
    except: return [], 500

def get_fathom_summary(recording_id):
    url = f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary"
    headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get("summary", {}).get("markdown_formatted")
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"סכם את הפגישה לעברית עסקית רהוטה. השתמש בבולטים ומספור. הכל חייב להיות מיושר לימין:\n\n{raw_text}"
        return model.generate_content(prompt).text
    except Exception as e: return f"שגיאה בעיבוד: {e}"

# =========================================================
# 4. טעינת קבצים וניווט
# =========================================================
try:
    projects = pd.read_excel("my_projects.xlsx")
    # הסרתי קבצים שלא בשימוש בקוד שהצגת כדי למנוע שגיאות טעינה
except:
    st.error("Missing Data Files"); st.stop()

if "current_page" not in st.session_state: st.session_state.current_page = "main"

# =========================================================
# 5. תצוגת דשבורד
# =========================================================

# --- דף פרויקט ---
if st.session_state.current_page == "project" or "proj" in st.query_params:
    p_name = st.query_params.get("proj", st.session_state.get("selected_project", "פרויקט"))
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה"):
        st.query_params.clear()
        st.session_state.current_page = "main"
        st.rerun()
    st.info(f"ניהול פרויקט {p_name} בטעינה...")

# --- דף ראשי ---
else:
    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
    
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
    
    col_img, col_greet = st.columns([1, 3])
    with col_img:
        # כאן תוכלי להוסיף את ה-Base64 של התמונה שלך
        st.markdown(f'<div style="text-align:left;"><img src="https://via.placeholder.com/130" class="profile-img"></div>', unsafe_allow_html=True)
    
    with col_greet:
        st.markdown(f"""
            <div style="text-align: right; margin-top: 20px;">
                <h3 style='margin-bottom:0;'>{greeting}, סיון!</h3>
                <p style='color:gray; font-size:1rem;'>
                    {now.strftime('%d/%m/%Y | %H:%M')} 
                    <span style='margin-right:15px; color:#4facfe; font-weight:600; border-right:2px solid #ddd; padding-right:15px;'>
                        {weather_info}
                    </span>
                </p>
            </div>
        """, unsafe_allow_html=True)

    col_r, col_l = st.columns(2)
    
    with col_r:
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים פעילים")
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'<a href="{p_url}" target="_self" style="text-decoration:none;"><div class="record-row"><b>{row["project_name"]}</b><span class="tag-blue">פעיל</span></div></a>', unsafe_allow_html=True)

    with col_l:
        with st.container(border=True):
            st.markdown("### ✨ סיכומי Fathom (שמורים)")
            
            saved_summaries = load_saved_summaries()
            f_items, _ = get_fathom_meetings()
            
            if f_items:
                for mtg in f_items:
                    rid = str(mtg.get('recording_id'))
                    title = mtg.get('title', 'פגישה ללא שם')
                    st.markdown(f"**📅 {title}**")
                    
                    match = saved_summaries[saved_summaries['recording_id'].astype(str) == rid]
                    
                    if not match.empty:
                        st.info(match.iloc[0]['summary'])
                    else:
                        if st.button("סכם ושמור פגישה 🪄", key=f"btn_{rid}"):
                            with st.spinner("מנתח..."):
                                raw = get_fathom_summary(rid)
                                if raw:
                                    refined = refine_with_ai(raw)
                                    save_summary_to_file(rid, refined)
                                    st.rerun()
            else:
                st.write("אין פגישות חדשות ב-Fathom")
