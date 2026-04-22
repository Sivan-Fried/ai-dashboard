import streamlit as st
import requests
import datetime
from zoneinfo import ZoneInfo

# 1. הגדרה ראשונית - חובה שורה ראשונה
st.set_page_config(layout="wide", page_title="Sivan Dashboard 2026")

# 2. פונקציית מזג אוויר נקייה
def get_weather():
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Petah Tikva&appid={api_key}&units=metric&lang=he"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return f"{round(data['main']['temp'])}°C | {data['weather'][0]['description']}"
    except: pass
    return "מידע זמין בפתח תקווה"

# 3. חישוב נתונים
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
weather_info = get_weather()

# 4. תצוגה (שימוש ב-st.container ו-st.columns במקום HTML מורכב)
with st.container():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title(f"{greeting}, סיון! 👋")
        st.write(f"### {now.strftime('%H:%M')} | {now.strftime('%d/%m/%Y')}")
    
    with col2:
        st.metric(label="📍 פתח תקווה", value=weather_info)

st.divider()

# 5. הצגת פרויקטים (בדיקה אם הקובץ קיים)
st.subheader("📁 הפרויקטים שלי")
try:
    import pandas as pd
    df = pd.read_excel("my_projects.xlsx")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.info("ממתין לקובץ הפרויקטים... (וודאי שהוא בגיט)")
