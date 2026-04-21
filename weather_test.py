import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# הגדרה ראשונה - חובה
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
                /* 1. ביטול מוחלט של כל מה שזז בסטרימליט */
                [data-testid="stHeader"], [data-testid="stDecoration"], footer, #MainMenu {{
                    display: none !important;
                }}

                /* 2. איפוס מכולות - השלב הקריטי */
                .stAppViewContainer, .stAppViewMain, .main, .block-container {{
                    padding: 0 !important;
                    margin: 0 !important;
                    height: 0 !important; /* מבטל את הגובה של המכולות המקוריות */
                }}

                /* 3. יצירת השכבה שלנו - דבוקה למעלה (Top: 0) */
                .ios-background {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: {bg} !important;
                    z-index: 999999;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding-top: 12vh;
                    color: white;
                    /* פונט דק ויוקרתי */
                    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
                    text-align: center;
                    overflow: hidden;
                }}

                .city-label {{ font-size: 36px; font-weight: 400; margin: 0; }}
                .temp-label {{ font-size: 110px; font-weight: 100; margin: -10px 0; letter-spacing: -3px; }}
                .desc-label {{ font-size: 24px; font-weight: 500; opacity: 0.9; }}
                
                /* 4. החזרת הזוהר (Glow) */
                .glow-icon {{
                    font-size: 100px;
                    margin-top: 30px;
                    color: {"#E0E0E0" if is_night else "#FFD700"};
                    /* הילה רכה ורחבה */
                    filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.5));
                }}
            </style>
            
            <div class="ios-background">
                <div class="city-label">{city}</div>
                <div class="temp-label">{temp}°</div>
                <div class="desc-label">{desc.capitalize()}</div>
                <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"} glow-icon"></i>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h2 style='text-align: center; margin-top: 45vh; font-family: sans-serif; color: #4facfe;'>מזהה מיקום...</h2>", unsafe_allow_html=True)
