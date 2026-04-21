import streamlit as st
import requests
import geocoder
import os

def get_weather_data():
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    if not api_key: return None
    try:
        g = geocoder.ip('me')
        lat, lon = g.latlng
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except: return None

# --- עיצוב סטייל אייפון ---
def apply_iphone_style(icon_code):
    # קביעת צבע רקע לפי יום (d) או לילה (n)
    is_night = "n" in icon_code
    if is_night:
        bg_color = "linear-gradient(180deg, #1a2a6c, #b21f1f, #fdbb2d)" # שקיעה/לילה
        text_color = "#ffffff"
    else:
        bg_color = "linear-gradient(180deg, #4facfe 0%, #00f2fe 100%)" # שמיים בהירים
        text_color = "#ffffff"

    st.markdown(f"""
        <style>
        .stApp {{
            background: {bg_color};
            color: {text_color};
        }}
        .weather-card {{
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            padding: 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        .temp {{
            font-size: 80px !important;
            font-weight: 200 !important;
            margin-bottom: 0px;
        }}
        .city {{
            font-size: 24px !important;
            font-weight: 500 !important;
        }}
        </style>
    """, unsafe_allow_value=True)

# --- תצוגה ---
st.set_page_config(page_title="מזג אוויר", page_icon="🌤️")

data = get_weather_data()

if data:
    icon_code = data['weather'][0]['icon']
    apply_iphone_style(icon_code)
    
    city = data.get('name', 'המיקום שלך')
    temp = round(data['main']['temp'])
    desc = data['weather'][0]['description']
    
    # הצגת ה"כרטיסיה"
    st.markdown(f"""
        <div class="weather-card">
            <p class="city">{city}</p>
            <h1 class="temp">{temp}°</h1>
            <p style="font-size: 20px;">{desc.capitalize()}</p>
            <img src="http://openweathermap.org/img/wn/{icon_code}@4x.png" width="150">
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("לא הצלחתי לטעון נתונים. ודאי שהמפתח תקין.")
