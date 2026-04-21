import streamlit as st
import requests
import geocoder
import os

# פונקציה חכמה שבודקת את המפתח בשני מקומות
def get_weather_data():
    # 1. ניסיון למשוך מהבאש (מקומי)
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # 2. אם לא נמצא בבאש, ניסיון למשוך מה-Secrets של סטרימליט (ענן)
    if not api_key:
        try:
            api_key = st.secrets["OPENWEATHER_API_KEY"]
        except:
            api_key = None

    if not api_key:
        st.error("שגיאה: לא נמצא API Key. ודאי שהגדרת אותו ב-Bash או ב-Secrets.")
        return None

    try:
        # זיהוי מיקום אוטומטי
        g = geocoder.ip('me')
        lat, lon = g.latlng
        
        # קריאה ל-API (Current Weather)
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
        st.error(f"שגיאה בטעינה: {e}")
        return None

# --- עיצוב הממשק ---
st.set_page_config(page_title="בדיקת מזג אוויר", page_icon="☀️")

st.title("☀️ בדיקת רכיב מזג אוויר")
st.write("הקוד בודק את המפתח בבאש המקומי או ב-Secrets של הענן.")

if st.button("טען נתונים עכשיו"):
    with st.spinner("מתחבר לשירות המטאורולוגי..."):
        weather = get_weather_data()
        
        if weather:
            # יצירת האייקון הצבעוני
            icon_url = f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png"
            
            st.divider()
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image(icon_url, width=100)
            
            with col2:
                st.header(f"{weather['temp']}°C")
                st.subheader(f"ב{weather['city']}")
                st.write(f"מצב השמיים: **{weather['description']}**")
            st.divider()
