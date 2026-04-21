import streamlit as st
import requests
import os
from streamlit_js_eval import get_geolocation

# פונקציה להבאת נתונים לפי קואורדינטות
def get_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
    try:
        return requests.get(url).json()
    except:
        return None

# הגדרות דף בסיסיות
st.set_page_config(page_title="מזג אוויר", page_icon="☀️", layout="centered")

# ביטול הקו הלבן והכותרת של סטרימליט
st.markdown("""
    <style>
    /* מחיקה מוחלטת של ה-Header של סטרימליט */
    header[data-testid="stHeader"], div[data-testid="stDecoration"], section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* מחיקת ה-padding העליון כדי שהעיצוב יתחיל מלמעלה */
    .main .block-container {
        padding-top: 2rem !important;
    }
    
    /* מניעת פדינג נוסף כשמעבירים layout ל-centered */
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# בקשת מיקום מהדפדפן
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    data = get_weather(lat, lon)
    
    if data and data.get('main'):
        temp = round(data['main']['temp'])
        
        # תרגום ידני לפתח תקווה אם השם חזר באנגלית
        city = data.get('name', 'פתח תקווה')
        if city.lower() in ['petah tikva', 'petah tiqwa']:
            city = "פתח תקווה"
            
        desc = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']
        is_night = "n" in icon_code
        
        # רקע דינמי
        bg = "linear-gradient(180deg, #1a2a6c, #2c5364)" if is_night else "linear-gradient(180deg, #4facfe, #00f2fe)"

        st.markdown(f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
            .stApp {{ background: {bg} !important; }}
            .iphone-card {{ color: white; text-align: center; font-family: -apple-system, sans-serif; }}
            .city-name {{ font-size: 40px; font-weight: 500; }}
            .temp-display {{ font-size: 110px; font-weight: 100; margin: -20px 0; }}
            .weather-desc {{ font-size: 24px; font-weight: 500; opacity: 0.9; }}
            .bi {{ font-size: 100px; margin-top: 30px; display: block; }}
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
