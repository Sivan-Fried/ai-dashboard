import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

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
                /* העלמת אלמנטים של המערכת */
                [data-testid="stHeader"], [data-testid="stDecoration"], footer {{
                    display: none !important;
                }}

                /* איפוס המכולה של סטרימליט וביטול הפס הלבן בכוח */
                .stApp {{
                    background: {bg} !important;
                    position: fixed;
                    width: 100vw;
                    height: 100vh;
                    top: 0;
                    left: 0;
                }}

                /* ה-CSS שאחראי על ביטול הרווח העליון */
                .main .block-container {{
                    padding: 0 !important;
                    margin-top: -100px !important; /* דוחף את כל התוכן למעלה מעבר לפס הלבן */
                }}

                .ios-screen {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    width: 100vw;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    text-align: center;
                }}

                .city-name {{ font-size: 36px; font-weight: 500; margin-bottom: 0; }}
                .temp-val {{ font-size: 110px; font-weight: 100; margin: -10px 0; letter-spacing: -3px; }}
                .weather-desc {{ font-size: 22px; font-weight: 500; opacity: 0.9; }}
                
                /* החזרת הזוהר המבוקש */
                .glow-icon {{
                    font-size: 100px;
                    margin-top: 30px;
                    color: {"#E0E0E0" if is_night else "#FFD700"};
                    filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.5));
                }}
            </style>
            
            <div class="ios-screen">
                <div class="city-name">{city}</div>
                <div class="temp-val">{temp}°</div>
                <div class="weather-desc">{desc.capitalize()}</div>
                <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"} glow-icon"></i>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp {background: #4facfe !important;}</style>", unsafe_allow_html=True)
    st.write("מזהה מיקום...")
