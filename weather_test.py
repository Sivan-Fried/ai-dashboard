import streamlit as st
import requests
import geocoder
import os

# פונקציה למשיכת נתונים לפי מיקום חי
def get_weather_data():
    api_key = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    try:
        # שליפת מיקום נוכחי לפי IP (הכי אמין להרצה מקומית ובענן)
        g = geocoder.ip('me')
        if not g.latlng:
            # גיבוי למקרה שה-IP חסום - מיקום ברירת מחדל (חולון)
            lat, lon = 32.0158, 34.7874
        else:
            lat, lon = g.latlng
            
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=he"
        return requests.get(url).json()
    except Exception as e:
        return None

data = get_weather_data()

if data:
    temp = round(data['main']['temp'])
    city = data.get('name', 'המיקום שלך')
    desc = data['weather'][0]['description']
    icon_code = data['weather'][0]['icon']
    
    # מיפוי אייקונים של Bootstrap למראה נקי
    icon_map = {
        "01d": "bi-sun-fill", "01n": "bi-moon-stars-fill",
        "02d": "bi-cloud-sun-fill", "02n": "bi-cloud-moon-fill",
        "03d": "bi-cloud-fill", "03n": "bi-cloud-fill",
        "04d": "bi-clouds-fill", "04n": "bi-clouds-fill",
        "09d": "bi-cloud-rain-heavy-fill", "10d": "bi-cloud-drizzle-fill",
        "11d": "bi-cloud-lightning-fill", "13d": "bi-snow", "50d": "bi-cloud-haze-fill"
    }
    bootstrap_icon = icon_map.get(icon_code, "bi-sun-fill")
    
    # צבע אייקון: צהוב לשמש, לבן לכל השאר
    icon_color = "#FFD700" if "sun" in bootstrap_icon else "#FFFFFF"
    
    # רקע דינמי: תכלת ליום, כחול כהה ללילה
    is_night = "n" in icon_code
    bg_gradient = "linear-gradient(180deg, #1a2a6c, #2c5364)" if is_night else "linear-gradient(180deg, #4facfe, #00f2fe)"

    st.markdown(f"""
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
        .stApp {{
            background: {bg_gradient} !important;
        }}
        header {{visibility: hidden;}}
        .main .block-container {{ padding-top: 5rem; }}
        
        .iphone-card {{
            color: white;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .city-name {{ font-size: 38px; font-weight: 500; margin-bottom: 0; }}
        .temp-display {{ font-size: 110px; font-weight: 100; margin: -15px 0; letter-spacing: -3px; }}
        .weather-desc {{ font-size: 24px; font-weight: 500; opacity: 0.9; }}
        .high-low {{ font-size: 20px; font-weight: 400; margin-top: 8px; opacity: 0.8; }}
        .main-icon {{ 
            font-size: 90px; 
            color: {icon_color}; 
            margin-top: 40px;
            filter: drop-shadow(0 0 15px {icon_color}88);
        }}
        </style>
        
        <div class="iphone-card">
            <div class="city-name">{city}</div>
            <div class="temp-display">{temp}°</div>
            <div class="weather-desc">{desc.capitalize()}</div>
            <div class="high-low">H:{temp+2}°  L:{temp-2}°</div>
            <div class="main-icon"><i class="bi {bootstrap_icon}"></i></div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("לא הצלחתי לזהות מיקום או למשוך נתונים.")
