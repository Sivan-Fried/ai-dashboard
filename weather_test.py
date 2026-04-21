import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# הגדרת דף בסיסית
st.set_page_config(page_title="Weather", layout="wide")

def get_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        return requests.get(url).json()
    except: return None

# שליפת מיקום
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    data = get_weather(lat, lon)
    
    if data and data.get('main'):
        temp = round(data['main']['temp'])
        city = data.get('name', 'פתח תקווה')
        if city.lower() in ['petah tikva', 'petah tiqwa']: city = "פתח תקווה"
        desc = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']
        is_night = "n" in icon_code
        bg = "linear-gradient(180deg, #1a2a6c, #2c5364)" if is_night else "linear-gradient(180deg, #4facfe, #00f2fe)"

        # CSS סופי ומדויק
        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                /* העלמה אגרסיבית של כל מה שקשור לסטרימליט */
                [data-testid="stHeader"], [data-testid="stDecoration"], footer, #MainMenu {{
                    display: none !important;
                }}

                /* איפוס מוחלט של הקונטיינר העליון */
                .stAppViewContainer {{
                    padding-top: 0 !important;
                }}
                
                .main .block-container {{
                    padding-top: 0 !important;
                    margin-top: -50px !important; /* דוחף הכל למעלה כדי לחסל את הפס */
                }}

                .stApp {{
                    background: {bg} !important;
                }}

                /* עיצוב הכרטיסייה עם הפונט של אפל */
                .iphone-screen {{
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    padding-top: 80px; /* רווח מדויק מהקצה העליון */
                    color: white;
                    /* שימוש בפונט מערכת הכי קרוב לאייפון */
                    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif;
                    text-align: center;
                }}

                .city {{ 
                    font-size: 34px; 
                    font-weight: 400; 
                    margin-bottom: 0; 
                }}
                
                .temp {{ 
                    font-size: 96px; 
                    font-weight: 100; 
                    margin: -10px 0; 
                    letter-spacing: -2px;
                }}
                
                .desc {{ 
                    font-size: 22px; 
                    font-weight: 500; 
                    opacity: 0.9;
                }}
                
                .icon-container {{ 
                    font-size: 90px; 
                    margin-top: 20px;
                    filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
                }}
            </style>
            
            <div class="iphone-screen">
                <div class="city">{city}</div>
                <div class="temp">{temp}°</div>
                <div class="weather-desc">{desc.capitalize()}</div>
                <div class="icon-container">
                    <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"}" 
                       style="color: {"#E0E0E0" if is_night else "#FFD700"}"></i>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h2 style='color: white; text-align: center; padding-top: 100px;'>מזהה מיקום...</h2>", unsafe_allow_html=True)
