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

st.set_page_config(page_title="מזג אוויר", page_icon="☀️", layout="wide")

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

        # הזרקת ה-CSS - ודאי שכל זה נכנס תחת st.markdown אחד
        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                /* מחיקת שאריות קוד מהמסך וביטול אלמנטים של סטרימליט */
                [data-testid="stHeader"], [data-testid="stDecoration"], footer {{
                    display: none !important;
                }}

                .stAppViewContainer {{
                    padding: 0 !important;
                }}

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
                    height: 100vh;
                    width: 100vw;
                }}

                .city-name {{ font-size: 45px; font-weight: 500; margin-top: -5vh; }} 
                .temp-display {{ font-size: 130px; font-weight: 100; margin: -10px 0; line-height: 1; }} 
                .weather-desc {{ font-size: 26px; font-weight: 500; opacity: 0.9; }} 
                .bi {{ font-size: 110px; margin-top: 30px; }}
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
    st.markdown("""
        <style>
            .stApp { background: #4facfe !important; }
            .loading { color: white; text-align: center; margin-top: 45vh; font-family: sans-serif; }
        </style>
        <div class="loading"><h1>מזהה מיקום...</h1></div>
    """, unsafe_allow_html=True)
