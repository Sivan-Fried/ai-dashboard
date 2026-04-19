import streamlit as st
import requests
import base64

st.set_page_config(page_title="Aman AI Dashboard", layout="wide")
st.title("🚀 Aman AI Dashboard")

# כאן את שותלת את המפתח החדש שהעתקת מ-Azure
PAT = "2Uyj5H2NCaQx8NJIFgEGBVS5grCDJgplnYx72IoIpqODRI4Zhy1wJQQJ99CDACAAAAAI9nwOAAAGAZDO4ETo"
ORGANIZATION = "amandigital"

def get_projects():
    auth_str = f":{PAT}"
    encoded_auth = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
    headers = {'Authorization': f'Basic {encoded_auth}'}
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/projects?api-version=6.0"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response
    except Exception as e:
        return str(e)

response = get_projects()

if hasattr(response, 'status_code'):
    if response.status_code == 200:
        projects = response.json().get('value', [])
        st.success(f"התחברנו! נמצאו {len(projects)} פרויקטים.")
        for p in projects:
            st.info(f"📁 פרויקט: {p['name']}")
    elif response.status_code == 203:
        st.error("שגיאה 203: הארגון עדיין חוסם. ודאי שהמפתח הוא החדש עם 'All organizations'.")
    else:
        st.warning(f"קוד שגיאה: {response.status_code}")
else:
    st.error(f"תקלה: {response}")
