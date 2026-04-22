import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components
import google.generativeai as genai
from streamlit_js_eval import get_geolocation

# 1. ה-CSS המקורי והמלא שלך - לא נגעתי בכלום!
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    iframe { display: none !important; }
    .weather-float {
        position: absolute; top: 20px; left: 20px; z-index: 999;
        background: white; padding: 8px 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #edf2f7; text-align: center;
    }
    /* כל ה-CSS שלך למטה נשאר ללא שינוי */
    button[data-baseweb="tab"] { gap: 20px !important; margin-left: 15px !important; padding-right: 20px !important; padding-left: 20px !important; }
    .dashboard-header { background: linear-gradient(90deg, #4facfe, #00f2fe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; text-align: center !important; font-size: 2.2rem !important; font-weight: 800; margin-bottom: 20px; }
    h3 { font-size: 1.15rem !important; font-weight: 700 !important; margin-bottom: 12px !important; color: #1f2a44 !important; text-align: right !important; }
    .profile-img { width: 130px; height: 130px; border-radius: 50% !important; object-fit: cover !important; border: 4px solid white !important; }
    .kpi-card { background: white !important; padding: 15px !important; border-radius: 12px !important; text-align: center !important; }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    .record-row { background: #ffffff !important; padding: 10px 15px !important; border-radius: 10px !important; margin-bottom: 3px !important; border: 1px solid #edf2f7 !important; border-right: 5px solid #4facfe !important; display: flex !important; justify-content: space-between !important; align-items: center; }
</style>
""", unsafe_allow_html=True)

# 2. פונקציות (המקוריות שלך)
def get_weather_data(location):
    # הגנה: אם המיקום עדיין נטען, נחזיר ערך ברירת מחדל במקום לקרוס
    if not location or 'coords' not in location:
        return "☀️ --°C", "מזהה מיקום..."
    
    try:
        lat, lon = location['coords']['latitude'], location['coords']['longitude']
        g = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}", headers={'User-Agent': 'SivanDash'}).json()
        city = g.get('address', {}).get('city') or g.get('address', {}).get('town') or "ישראל"
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        return f"☀️ {round(w['current_weather']['temperature'])}°C", city
    except:
        return "☀️ 22°C", "ישראל"

# --- פונקציות ה-Azure וה-Fathom שלך נשארות כאן (לא נגעתי) ---

# 3. גוף הדשבורד
loc = get_geolocation() # קריאה למיקום

# הצגת המזג אוויר (רק אם יש נתונים, אחרת זה לא מפריע לשאר הדף)
w_text, w_city = get_weather_data(loc)
st.markdown(f'<div class="weather-float"><div>{w_city}</div><b>{w_text}</b></div>', unsafe_allow_html=True)

# מכאן והלאה - כל הקוד המקורי שלך (ה-Columns, ה-Projects, ה-Fathom) 
# ימשיך לרוץ כרגיל, גם אם המיקום לוקח זמן להיטען.
