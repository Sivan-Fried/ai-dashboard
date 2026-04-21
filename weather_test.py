import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# הגדרת דף בסיסית - חייב להיות בשורה הראשונה
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

        # CSS שפשוט "מוחק" את סטרימליט מהמסך
        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                /* העלמת כל רכיבי המערכת של סטרימליט */
                header, [data-testid="stHeader"], [data-testid="stDecoration"], footer {{
                    display: none !important;
                }}

                /* איפוס מוחלט של כל המרווחים */
                .stApp {{
                    background: {bg} !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                .main .block-container {{
                    max-width: 100% !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }}

                /* כרטיסיית האייפון - תופסת את כל המסך */
                .iphone-screen {{
                    height: 100vh;
                    width: 100vw;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    padding-top: 15vh;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    text-align: center;
                }}

                .city {{ font-size: 38px; font-weight: 400; margin: 0; }}
                .temp {{ font-size: 110px; font-weight: 100; margin: -10px 0; }}
                .desc {{ font-size: 24px; font-weight: 500; opacity: 0.9; }}
                .icon {{ font-size: 100px; margin-top: 30px; }}
            </style>
            
            <div class="iphone-screen">
                <h1 class="city">{city}</h1>
                <div class="temp">{temp}°</div>
                <div class="desc">{desc.capitalize()}</div>
                <div class="icon">
                    <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"}" 
                       style="color: {"#E0E0E0" if is_night else "#FFD700"}"></i>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp {background: #4facfe !important;}</style>", unsafe_allow_html=True)
    st.write("ממתין לאישור מיקום...")
