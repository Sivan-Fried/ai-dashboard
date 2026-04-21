import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

def get_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        return requests.get(url).json()
    except: return None

# הגדרת layout רחב כדי למנוע מרווחים מהצדדים
st.set_page_config(page_title="מזג אוויר", page_icon="☀️", layout="wide")

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

        # CSS שמשתלט על כל המסך באמת
        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
            /* העלמה מוחלטת של כל המסגרת של סטרימליט */
            [data-testid="stHeader"], [data-testid="stDecoration"], footer {{
                display: none !important;
            }}
            
            /* קיבוע הרקע והתוכן לכל שטח המסך */
            .stApp {{
                background: {bg} !important;
                position: fixed;
                width: 100vw;
                height: 100vh;
                top: 0;
                left: 0;
                overflow: hidden;
            }}

            .iphone-card {{
                color: white;
                text-align: center;
                font-family: -apple-system, system-ui, sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh; /* ממרכז את הכל בדיוק לאמצע המסך */
            }}

            .city-name {{ font-size: 45px; font-weight: 500; margin-top: -10vh; }}
            .temp-display {{ font-size: 130px; font-weight: 100; margin: -10px 0; }}
            .weather-desc {{ font-size: 26px; font-weight: 500; opacity: 0.9; }}
            .bi {{ font-size: 110px; margin-top: 40px; }}
            </style>
            
            <div class="iphone-card">
                <div class="city-name">{city}</div>
                <div class="temp-display">{temp}°</div>
                <div class="weather-desc">{desc.capitalize()}</div>
                <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"}" 
                   style="color: {"#E0E0E0" if is_night else "#FFD700"}"></i>
            </div>
        """, unsafe_allow_html=True)
else:
    # רקע זמני בזמן טעינה כדי שלא יהיה לבן בעיניים
    st.markdown("""<style>.stApp { background: #4facfe !important; }</style>""", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; text-align: center; margin-top: 45vh;'>מזהה מיקום...</h2>", unsafe_allow_html=True)
