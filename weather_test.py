import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# פונקציה שמביאה נתונים לפי קואורדינטות מדויקות
def get_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        return requests.get(url).json()
    except:
        return None

st.set_page_config(page_title="Weather", page_icon="☀️")

# השלב החכם: בקשת מיקום מהדפדפן (Browser Geolocation)
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    data = get_weather(lat, lon)
    
    if data and data.get('main'):
        temp = round(data['main']['temp'])
        city = data.get('name', 'מיקום נוכחי')
        desc = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']
        is_night = "n" in icon_code
        bg = "linear-gradient(180deg, #1a2a6c, #2c5364)" if is_night else "linear-gradient(180deg, #4facfe, #00f2fe)"

        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
            .stApp {{ background: {bg} !important; }}
            header {{visibility: hidden;}}
            .iphone-card {{ color: white; text-align: center; font-family: -apple-system, sans-serif; margin-top: 50px; }}
            .city-name {{ font-size: 40px; font-weight: 500; }}
            .temp-display {{ font-size: 110px; font-weight: 100; margin: -20px 0; }}
            .bi {{ font-size: 80px; margin-top: 20px; display: block; }}
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
    st.markdown("<h3 style='color: white; text-align: center;'>אנא אשר גישה למיקום בדפדפן כדי לראות מזג אוויר מדויק...</h3>", unsafe_allow_html=True)
