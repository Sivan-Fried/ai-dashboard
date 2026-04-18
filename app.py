import streamlit as st
import requests

st.title("בדיקת הרשאות API")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    if st.button("בדוק מודלים זמינים"):
        # פקודה שמבקשת מגוגל להראות לנו מה המפתח הזה "רואה"
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                models_data = res.json()
                st.success("המפתח תקין! הנה המודלים שאת יכולה להשתמש בהם:")
                # מציג את רשימת המודלים שגוגל נותנת לך
                for m in models_data.get('models', []):
                    st.code(m['name'])
            else:
                st.error(f"שגיאה {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"שגיאה טכנית: {e}")
else:
    st.error("חסר API Key ב-Secrets!")
