import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# הגדרה ראשונה - חייבת להיותwide
st.set_page_config(page_title="Weather", layout="wide")

def get_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        return requests.get(url).json()
    except: return None

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

        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                /* השמדת כל זכר לממשק של סטרימליט */
                iframe {{ display: none; }}
                header, footer, [data-testid="stHeader"], [data-testid="stDecoration"] {{
                    display: none !important;
                    height: 0 !important;
                }}

                /* יצירת שכבה עליונה שדורסת את הפס הלבן */
                .full-screen-overlay {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: {bg};
                    z-index: 999999;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    padding-top: 12vh;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    text-align: center;
                }}

                .city-text {{ font-size: 36px; font-weight: 400; margin: 0; letter-spacing: 0.5px; }}
                .temp-text {{ font-size: 115px; font-weight: 100; margin: -15px 0; letter-spacing: -4px; }}
                .desc-text {{ font-size: 24px; font-weight: 500; opacity: 0.9; }}
                .weather-icon {{ font-size: 100px; margin-top: 30px; }}

                /* איפוס ה-body של הדף למניעת גלילה */
                body {{ overflow: hidden; }}
            </style>
            
            <div class="full-screen-overlay">
                <div class="city-text">{city}</div>
                <div class="temp-text">{temp}°</div>
                <div class="desc-text">{desc.capitalize()}</div>
                <div class="weather-icon">
                    <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"}" 
                       style="color: {"#E0E0E0" if is_night else "#FFD700"}"></i>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h2 style='text-align: center; margin-top: 45vh; font-family: sans-serif;'>מזהה מיקום...</h2>", unsafe_allow_html=True)
