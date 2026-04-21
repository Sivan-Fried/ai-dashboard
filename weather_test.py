import streamlit as st
import requests
import geocoder

# פונקציה להבאת נתונים - ללא המפתח בקוד
def get_weather_data():
    try:
        # שליפת המפתח מה-Secrets של סטרימליט
        api_key = st.secrets["OPENWEATHER_API_KEY"]
        
        # זיהוי מיקום אוטומטי לפי IP
        g = geocoder.ip('me')
        lat, lon = g.latlng
        city = g.city if g.city else "Israel"

        # קריאה ל-API של OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
        
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            return {
                "city": city,
                "temp": round(data['main']['temp']),
                "description": data['weather'][0]['description'],
                "icon_code": data['weather'][0]['icon']
            }
        else:
            st.error(f"שגיאת API: {data.get('message')}")
            return None
    except Exception as e:
        st.error(f"שגיאה כללית: {e}")
        return None

# --- תצוגה בדף הבדיקה ---
st.title("☀️ בדיקת רכיב מזג אוויר")

if st.button("טען מזג אוויר"):
    weather = get_weather_data()
    
    if weather:
        # יצירת הלינק לאייקון צבעוני (השתמשתי ב-@2x בשביל איכות גבוהה)
        icon_url = f"http://openweathermap.org/img/wn/{weather['icon_code']}@2x.png"
        
        # עיצוב בסיסי לראות שזה עובד
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(icon_url, width=100)
        with col2:
            st.metric(label=f"מזג האוויר ב{weather['city']}", value=f"{weather['temp']}°C")
            st.write(f"סטטוס: **{weather['description']}**")
    else:
        st.warning("לא התקבלו נתונים. ודאי שהגדרת את ה-Secrets ושעבר מספיק זמן מאז יצירת ה-API Key.")
