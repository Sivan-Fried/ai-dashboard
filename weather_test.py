import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# חובה בשורה הראשונה
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
                /* הסרה מוחלטת של אלמנטים של המערכת */
                [data-testid="stHeader"], [data-testid="stDecoration"], footer {{
                    display: none !important;
                }}

                /* ביטול הפס הלבן ואיפוס המרחב */
                .stApp {{
                    background: {bg} !important;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                }}

                .main .block-container {{
                    padding: 0 !important;
                    margin: 0 !important;
                }}

                /* יצירת שכבת המגן שתחסום את הפס */
                .ios-container {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    z-index: 99999;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding-top: 10vh;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
                    text-align: center;
                }}

                .city {{ font-size: 38px; font-weight: 500; margin-bottom: 0; }}
                .temp {{ font-size: 115px; font-weight: 100; margin: -10px 0; letter-spacing: -4px; }}
                .desc {{ font-size: 24px; font-weight: 400; opacity: 0.9; }}

                /* האפקט הזוהר המבוקש */
                .glow-icon {{
                    font-size: 100px;
                    margin-top: 35px;
                    color: {"#E0E0E0" if is_night else "#FFD700"};
                    /* הילה רכה ורחבה */
                    filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.5));
                    -webkit-filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.5));
                }}
            </style>
            
            <div class="ios-container">
                <div class="city">{city}</div>
                <div class="temp">{temp}°</div>
                <div class="desc">{desc.capitalize()}</div>
                <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"} glow-icon"></i>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp {background: #4facfe !important;}</style>", unsafe_allow_html=True)
