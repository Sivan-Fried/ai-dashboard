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
        
        # זיהוי שם העיר מה-API
        city_from_api = data.get('name', '')
        if not city_from_api or city_from_api.lower() in ['petah tikva', 'petah tiqwa']:
            city = "פתח תקווה"
        else:
            city = city_from_api
            
        desc = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']
        is_night = "n" in icon_code
        bg = "linear-gradient(180deg, #1a2a6c, #2c5364)" if is_night else "linear-gradient(180deg, #4facfe, #00f2fe)"

        st.markdown(f"""
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            
            <style>
                [data-testid="stHeader"], [data-testid="stDecoration"], footer {{ display: none !important; }}

                .stApp {{
                    background: {bg} !important;
                    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                }}

                .stAppViewContainer, .stAppViewMain, .main, .block-container {{
                    padding: 0 !important; margin: 0 !important; height: 0 !important;
                }}

                .ios-background {{
                    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                    z-index: 999999; display: flex; flex-direction: column;
                    align-items: center; padding-top: 10vh; color: white;
                    font-family: 'Inter', sans-serif !important; text-align: center;
                }}

                .city-label {{ 
                    font-size: 36px; font-weight: 300; margin-bottom: 0; 
                }}
                
                .temp-container {{
                    display: flex; align-items: flex-start; justify-content: center;
                    margin: -10px 0;
                }}

                .temp-num {{ 
                    font-size: 115px; font-weight: 100; letter-spacing: -5px; 
                }}
                
                /* הקטנת סימן המעלות */
                .degree-symbol {{ 
                    font-size: 45px; font-weight: 200; margin-top: 25px; margin-left: 2px;
                }}
                
                .desc-label {{ 
                    font-size: 24px; font-weight: 400; opacity: 0.9; margin-top: -10px;
                }}
                
                .glow-icon {{
                    font-size: 100px; margin-top: 40px;
                    color: {"#E0E0E0" if is_night else "#FFD700"};
                    filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.5));
                }}
            </style>
            
            <div class="ios-background">
                <div class="city-label">{city}</div>
                <div class="temp-container">
                    <span class="temp-num">{temp}</span>
                    <span class="degree-symbol">°</span>
                </div>
                <div class="desc-label">{desc.capitalize()}</div>
                <i class="bi {"bi-moon-stars-fill" if is_night else "bi-sun-fill"} glow-icon"></i>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h2 style='text-align: center; margin-top: 45vh; color: white;'>מזהה מיקום...</h2>", unsafe_allow_html=True)
