import os

def get_weather_data():
    # קודם כל מנסה למשוך מהבאש (מקומי), אם לא מוצא - מנסה מה-Secrets (ענן)
    api_key = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY")
    
    if not api_key:
        st.error("לא נמצא API Key בבאש וגם לא ב-Secrets")
        return None

    try:
        g = geocoder.ip('me')
        lat, lon = g.latlng
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
        st.error(f"שגיאה: {e}")
        return None
