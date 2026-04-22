import streamlit as st
import requests
import pandas as pd
import datetime
from zoneinfo import ZoneInfo
import google.generativeai as genai

# הגדרת דף - חובה שורה ראשונה
st.set_page_config(layout="wide", page_title="Sivan Dashboard 2026")

# --- פונקציות תשתית ---
def get_weather():
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Petah Tikva&appid={api_key}&units=metric&lang=he"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return f"{round(data['main']['temp'])}°C | {data['weather'][0]['description']}"
    except: pass
    return "מידע מזג אוויר לא זמין"

def load_summaries():
    try: return pd.read_excel("fathom_summaries.xlsx")
    except: return pd.DataFrame(columns=["recording_id", "summary", "date"])

# --- חישוב נתונים ---
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
weather_info = get_weather()

# --- עיצוב (CSS מודרני) ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; direction: rtl; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #4facfe !important; }
    .header-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-right: 10px solid #4facfe;
        text-align: right; margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- תצוגת ראש הדף ---
st.markdown(f"""
<div class="header-card">
    <h1 style='margin:0;'>{greeting}, סיון! 👋</h1>
    <p style='margin:5px 0; color:#64748b; font-size:1.1rem;'>
        {now.strftime('%H:%M')} | {now.strftime('%d/%m/%Y')}
    </p>
</div>
""", unsafe_allow_html=True)

# הצגת מזג אוויר ב-Metric נקי של סטרימליט (כדי שלא יתקע)
st.columns([3, 1])[1].metric("📍 פתח תקווה", weather_info)

st.divider()

# --- תוכן הדשבורד ---
col_r, col_l = st.columns(2)

with col_r:
    st.subheader("📁 הפרויקטים שלי")
    try:
        df_p = pd.read_excel("my_projects.xlsx")
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    except: st.info("מעלה נתוני פרויקטים...")

with col_l:
    st.subheader("✨ סיכומי פגישות")
    # כאן תבוא הלוגיקה של Fathom וה-Cache
    st.write("מתחבר ל-Fathom...")
