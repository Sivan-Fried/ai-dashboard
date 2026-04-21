import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# הגדרת דף - wide עוזר לבטל מגבלות רוחב
st.set_page_config(page_title="Weather", layout="wide")

def get_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        return requests.get(url).json()
    except: return None

# זיהוי מיקום
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

        # CSS שדורס כל פיקסל של סטרימליט
        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                /* העלמה מוחלטת של כל המסגרות */
                [data-testid="stHeader"], [data-testid="stDecoration"], footer, #MainMenu {{
                    display: none !important;
                }}

                /* איפוס מוחלט של כל מיכל אפשרי של סטרימליט */
                .stApp, .stAppViewContainer, .stAppViewMain, .main, .block-container {{
                    margin: 0 !important;
                    padding: 0 !important;
                    top: 0 !important;
                }}

                /* מתיחת הרקע על הכל */
                .stApp {{
                    background: {bg} !important;
                    height: 100vh;
                    width: 100vw;
                    position: fixed;
                }}

                /* עיצוב האייפון */
                .iphone-layout {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    padding-top: 10vh;
                }}

                .city-name {{ font-size: 34px; font-weight: 400; margin: 0; }}
                .temp-num {{ font-size: 110px; font-weight: 100; margin: -10px 0; letter-spacing: -3px; }}
                .weather-text {{ font-size: 24px; font-weight: 500; opacity: 0.9; }}
                .weather-icon {{ font-size: 100px; margin-top: 20px; }}
            </style>
            
            <div class="iphone-layout">
                <div class="city-name">{city}</div>
                <div class="temp-num">{temp}°</div>
                <div class="weather-text">{desc.capitalize()}</div>
                <div class="weather-icon">
                    <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"}" 
                       style="color: {"#E0E0E0" if is_night else "#FFD700"}"></i>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h2 style='color: white; text-align: center; padding-top: 40vh; font-family: sans-serif;'>מזהה מיקום...</h2>", unsafe_allow_html=True)
    st.markdown("<style>.stApp { background: #4facfe !important; }</style>", unsafe_allow_html=True)
