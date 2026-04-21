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

        # CSS שדורס כל פיקסל של סטרימליט
        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                /* העלמה אגרסיבית של כל מה שקשור לסטרימליט */
                iframe {{
                    border: none !important;
                    display: none;
                }}
                
                header, [data-testid="stHeader"], [data-testid="stDecoration"], footer {{
                    display: none !important;
                    height: 0 !important;
                }}
                
                body {{
                    overflow: hidden !important;
                }}
                
                /* מתיחת הרקע על הכל */
                .stApp {{
                    background: {bg} !important;
                    height: 100vh;
                    width: 100vw;
                    position: fixed;
                    top: 0;
                    left: 0;
                    z-index: 1;
                }}

                /* עיצוב הכרטיסייה */
                .iphone-screen {{
                    height: 100vh;
                    width: 100vw;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    padding-top: 10vh;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    text-align: center;
                    z-index: 2;
                }}

                .city-name {{ font-size: 38px; font-weight: 400; margin: 0; }}
                .temp-num {{ font-size: 110px; font-weight: 100; margin: -10px 0; }}
                .weather-text {{ font-size: 24px; font-weight: 500; opacity: 0.9; }}
                
                /* קונטיינר מיוחד לסמל עם אפקט זוהר */
                .weather-icon-container {{
                    margin-top: 30px;
                    width: 150px; /* גודל המכולה משפיע על גבולות ההילה */
                    height: 150px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}

                .weather-icon-glowing {{
                    font-size: 100px;
                    color: {"#E0E0E0" if is_night else "#FFD700"} !important;
                    /* שימוש ב-filter: drop-shadow כדי ליצור אפקט זוהר סביב הסמל */
                    filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.6)) !important;
                }}
            </style>
            
            <div class="iphone-screen">
                <div class="city-name">{city}</div>
                <div class="temp-num">{temp}°</div>
                <div class="weather-text">{desc.capitalize()}</div>
                <div class="weather-icon-container">
                    <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"} weather-icon-glowing"></i>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h2 style='color: white; text-align: center; padding-top: 100px;'>מזהה מיקום...</h2>", unsafe_allow_html=True)
