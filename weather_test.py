import streamlit as st
import requests
import geocoder
import os

def get_weather_data():
    # בדיקה בשני מקומות: קודם בבאש (מקומי) ואז ב-Secrets (ענן)
    api_key = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY")
    
    if not api_key:
        st.error("שגיאה: לא נמצא API Key. ודאי שהגדרת אותו ב-Bash או ב-Secrets.")
        return None

    try:
        # זיהוי מיקום אוטומטי לפי IP
        g = geocoder.ip('me')
        lat, lon = g.latlng
        
        # קריאה ל-API של OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
        
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            return {
                "city": data.get('name', 'Israel'),
                "temp": round(data['main']['temp']),
                "description": data['weather'][0]['description'],
                "icon": data['weather'][0]['icon']
            }
        else:
            st.error(f"שגיאת API: {data.get('message')}")
            return None
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {e}")
        return None

# --- עיצוב דף הבדיקה ---
st.set_page_config(page_title="Weather Test", page_icon="☀️")
st.title("☀️ בדיקת רכיב מזג אוויר")

st.info("הקוד מחפש כעת את המפתח ב-Bash (מקומי) או ב-Secrets (ענן).")

if st.button("טען נתונים"):
    weather = get_weather_data()
    if weather:
        icon_url = f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png"
        
        st.divider()
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(icon_url, width=80)
        with col2:
            st.metric(label=f"מזג אוויר ב{weather['city']}", value=f"{weather['temp']}°C")
            st.write(f"מצב השמיים: **{weather['description']}**")
        st.divider()
