import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
import google.generativeai as genai
from streamlit_js_eval import get_geolocation # הוספתי את זה

# =========================================================
# 1. פונקציות ניהול נתונים (סיכומים קבועים)
# =========================================================

def load_saved_summaries():
    try:
        return pd.read_excel("fathom_summaries.xlsx")
    except:
        return pd.DataFrame(columns=["recording_id", "summary", "date"])

def save_summary_to_file(rec_id, summary_text):
    df = load_saved_summaries()
    # בדיקה אם כבר קיים כדי לא לכפול
    if rec_id not in df['recording_id'].values:
        new_row = pd.DataFrame([{
            "recording_id": rec_id,
            "summary": summary_text,
            "date": datetime.datetime.now().strftime("%d/%m/%Y")
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel("fathom_summaries.xlsx", index=False)

# =========================================================
# 2. הגדרות דף ועיצוב
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan")

# (כאן נכנס כל ה-CSS שלך מהקוד הקודם, כולל התיקון ליישור לימין)
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    .stInfo, [data-testid="stNotification"] { text-align: right !important; direction: rtl !important; }
    .stInfo ul, .stInfo ol { direction: rtl !important; text-align: right !important; padding-right: 1.5rem !important; }
    /* ... שאר ה-CSS שלך ... */
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. פונקציות מזג אוויר (מבוסס מיקום כמו שעבד לך)
# =========================================================

def get_weather_by_coords(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        data = requests.get(url, timeout=5).json()
        if data and data.get('main'):
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            return f"{temp}°C | {desc}"
    except: return None
    return None

# =========================================================
# 4. גוף הדשבורד
# =========================================================

# זיהוי מיקום (יפעיל את מזג האוויר רק כשמזוהה)
loc = get_geolocation()
weather_display = "מתחבר למזג אוויר..."
if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    weather_display = get_weather_by_coords(lat, lon) or "לא זמין"

# --- כותרת וברכה ---
st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

p1, p2, p3 = st.columns([1.2, 1, 1.8])
# (קוד הפרופיל שלך...)
with p3: 
    st.markdown(f"""
        <div>
            <h3 style='margin-bottom:0;'>{greeting}, סיון!</h3>
            <p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')} | <span style='color:#4facfe;'>{weather_display}</span></p>
        </div>
    """, unsafe_allow_html=True)

# ... (חלקי המשימות והפרויקטים נשארים אותו דבר) ...

# =========================================================
# 5. אזור Fathom עם ה-Cache הקבוע
# =========================================================
with col_left:
    with st.container(border=True):
        st.markdown("### ✨ סיכומי פגישות Fathom")
        
        saved_df = load_saved_summaries()
        meetings_list = st.session_state.get('fathom_meetings', [])
        
        if not meetings_list:
            items, status = get_fathom_meetings() # הפונקציה הקיימת שלך
            if status == 200: st.session_state['fathom_meetings'] = items
            meetings_list = st.session_state.get('fathom_meetings', [])

        for idx, mtg in enumerate(meetings_list):
            rec_id = str(mtg.get('recording_id'))
            title = mtg.get('title') or "פגישה"
            
            st.markdown(f'<div class="record-row"><b>📅 {title}</b></div>', unsafe_allow_html=True)

            # בדיקה: האם הסיכום קיים באקסל?
            existing_summary = saved_df[saved_df['recording_id'].astype(str) == rec_id]
            
            if not existing_summary.empty:
                # מציג ישר מהאקסל - בלי לבזבז קריאות AI!
                st.info(existing_summary.iloc[0]['summary'])
            else:
                # רק אם לא קיים, מציע ליצור
                if st.button("צור סיכום חדש 🪄", key=f"gen_{rec_id}"):
                    with st.spinner("מנתח פעם ראשונה ושומר..."):
                        raw = get_fathom_summary(rec_id)
                        if raw:
                            new_summary = refine_with_ai(raw)
                            save_summary_to_file(rec_id, new_summary) # שמירה לאקסל
                            st.rerun()
