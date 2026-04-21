import streamlit as st
import requests
import geocoder
import os

# פונקציה לנתונים
def get_weather_data():
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    try:
        g = geocoder.ip('me')
        lat, lon = g.latlng
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
        return requests.get(url).json()
    except: return None

data = get_weather_data()

if data:
    temp = round(data['main']['temp'])
    city = data.get('name', 'חולון')
    desc = data['weather'][0]['description']
    icon_code = data['weather'][0]['icon']
    
    # קביעת צבעים לפי יום/לילה
    is_night = "n" in icon_code
    bg_gradient = "linear-gradient(180deg, #0f2027, #203a43, #2c5364)" if is_night else "linear-gradient(180deg, #4facfe 0%, #00f2fe 100%)"

    # הזרקת ה-CSS הכי "אלים" שיש כדי לדרוס את סטרימליט
    st.markdown(f"""
        <style>
        /* מנקה את כל הרקע של סטרימליט */
        .stApp {{
            background: {bg_gradient} !important;
        }}
        header {{visibility: hidden;}}
        .main .block-container {{
            padding-top: 2rem;
            max-width: 400px;
        }}
        
        /* כרטיסיית האייפון */
        .iphone-card {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: white;
            text-align: center;
            padding: 40px 20px;
            border-radius: 40px;
            /* בלי רקע לכרטיסייה, פשוט טקסט על הרקע המדורג כמו ב-iOS */
        }}
        
        .city-name {{ font-size: 34px; font-weight: 400; margin-bottom: 0; }}
        .temp-display {{ font-size: 96px; font-weight: 100; margin: 10px 0; letter-spacing: -2px; }}
        .weather-desc {{ font-size: 22px; font-weight: 500; opacity: 0.9; }}
        .high-low {{ font-size: 18px; font-weight: 500; margin-top: 10px; }}
        
        /* ביטול פדינגים מיותרים */
        div[data-testid="stVerticalBlock"] > div {{ padding: 0 !important; }}
        </style>
        
        <div class="iphone-card">
            <div class="city-name">{city}</div>
            <div class="temp-display">{temp}°</div>
            <div class="weather-desc">{desc.capitalize()}</div>
            <div class="high-low">H:{temp+2}°  L:{temp-3}°</div>
            <img src="http://openweathermap.org/img/wn/{icon_code}@4x.png" style="width: 180px; margin-top: 20px;">
        </div>
    """, unsafe_allow_html=True)
else:
    st.write("משהו השתבש בטעינה...")
