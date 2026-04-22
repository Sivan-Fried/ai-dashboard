import streamlit as st
import requests
import datetime

# שורה ראשונה וזהו!
st.set_page_config(layout="wide")

# פונקציית בדיקה הכי פשוטה בעולם
def check_weather():
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "שגיאה: מפתח API לא נמצא ב-Secrets"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Petah Tikva&appid={api_key}&units=metric&lang=he"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return f"מזג אוויר: {data['main']['temp']} מעלות בפתח תקווה"
        else:
            return f"שגיאת API: {r.status_code}"
    except Exception as e:
        return f"שגיאת תקשורת: {str(e)}"

# הצגת נתונים בסיסיים ללא עיצוב
st.title("בדיקת דשבורד")
res = check_weather()
st.write(f"### {res}") # זה חייב להופיע!

st.divider()

# המשך הקוד שלך...
