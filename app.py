import streamlit as st
import requests
import pandas as pd
import datetime
from zoneinfo import ZoneInfo
import google.generativeai as genai
from streamlit_js_eval import get_geolocation

# 1. הגדרות דף - חובה שורה ראשונה
st.set_page_config(layout="wide", page_title="Dashboard Sivan")

# --- פונקציות תשתית (מזג אוויר וארכיון) ---
def get_weather(lat, lon):
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
    return None

def load_summaries():
    try: return pd.read_excel("fathom_summaries.xlsx")
    except: return pd.DataFrame(columns=["recording_id", "summary", "date"])

def save_summary_to_file(rec_id, summary_text):
    df = load_summaries()
    rec_id = str(rec_id)
    if rec_id not in df['recording_id'].astype(str).values:
        new_row = pd.DataFrame([{"recording_id": rec_id, "summary": summary_text, "date": datetime.datetime.now().strftime("%d/%m/%Y")}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel("fathom_summaries.xlsx", index=False)

# --- שליפת נתונים בזמן אמת ---
loc = get_geolocation()
weather_info = "טוען מיקום..."
if loc:
    weather_info = get_weather(loc['coords']['latitude'], loc['coords']['longitude']) or "פתח תקווה"

now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

# --- עיצוב (CSS מקורי שלך עם תיקון RTL) ---
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    .stMarkdown, .stInfo, [data-testid="stNotification"] { text-align: right !important; direction: rtl !important; }
    .stInfo ul, .stInfo ol { direction: rtl !important; text-align: right !important; padding-right: 1.5rem !important; }
    
    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-size: 2.2rem; font-weight: 800; margin-bottom: 20px;
    }
    
    .record-row {
        background: white; padding: 12px; border-radius: 10px; margin-bottom: 5px;
        border-right: 5px solid #4facfe; display: flex; justify-content: space-between; align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# --- כותרת וברכה ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

col_greet = st.columns(1)[0]
with col_greet:
    st.markdown(f"""
        <div style="text-align: right; padding: 15px; background: white; border-radius: 15px; border-right: 10px solid #4facfe;">
            <h2 style='margin:0;'>{greeting}, סיון! 👋</h2>
            <p style='color:gray; font-size:1.1rem; margin:5px 0;'>
                <b>{now.strftime('%H:%M')}</b> | {now.strftime('%d/%m/%Y')} | 
                <span style='color:#4facfe; font-weight:600;'>📍 {weather_info}</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- פריסת הדשבורד ---
col_r, col_l = st.columns(2)

with col_r:
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים פעילים")
        try:
            projects = pd.read_excel("my_projects.xlsx")
            for _, row in projects.iterrows():
                st.markdown(f'<div class="record-row"><b>{row["project_name"]}</b></div>', unsafe_allow_html=True)
        except: st.info("מעלה נתוני פרויקטים...")

with col_l:
    with st.container(border=True):
        st.markdown("### ✨ סיכומי פגישות Fathom")
        
        saved_summaries = load_summaries()
        
        # כאן צריכה להיות הפונקציה שלך get_fathom_meetings
        # למטרת הקוד 1:1, אני מניח שזו הקריאה ל-API
        try:
            url = "https://api.fathom.ai/external/v1/meetings"
            headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"]}
            meetings = requests.get(url, headers=headers).json().get('items', [])[:5]
            
            for mtg in meetings:
                rid = str(mtg.get('recording_id'))
                st.markdown(f"**📅 {mtg.get('title', 'פגישה')}**")
                
                match = saved_summaries[saved_summaries['recording_id'].astype(str) == rid]
                if not match.empty:
                    st.info(match.iloc[0]['summary'])
                else:
                    if st.button("סכם ושמור פגישה 🪄", key=f"btn_{rid}"):
                        # לוגיקת Gemini וסיכום
                        st.write("מנתח ושומר...")
                        # כאן תבוא הפונקציה refine_with_ai(raw)
        except:
            st.warning("לא הצלחתי להתחבר ל-Fathom כרגע.")
