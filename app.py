import streamlit as st
import pandas as pd
import requests
import json
import base64
import os
import datetime

# הגדרת עמוד
st.set_page_config(layout="wide", page_title="AI Dashboard Stable")

# עיצוב CSS
st.markdown("""
<style>
body, .stApp { background-color: #f2f4f7; }
.card {
    background:white; padding:15px; border-radius:10px;
    margin-bottom:10px; border:1px solid #eee;
    direction:rtl; text-align:right;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
h1, h2, h3 { color:#1f2a44; text-align:right; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)



# =========================
# פרופיל יציב – תמונה באמצע + טקסט משמאל
# =========================
import datetime
import base64

# --- תמונה (כמו שהיה) ---
def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("profile.png")

# --- ברכה ---
import datetime
from zoneinfo import ZoneInfo

# זמן ישראל (בלי ספריות חיצוניות)
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))

hour = now.hour

if 5 <= hour < 12:
    greeting = "בוקר טוב"
elif 12 <= hour < 18:
    greeting = "צהריים טובים"
elif 18 <= hour < 22:
    greeting = "ערב טוב"
else:
    greeting = "לילה טוב"

date_str = now.strftime("%d/%m/%Y %H:%M")

# =========================
# פריסה נכונה (הפתרון האמיתי)
# =========================
left, center, right = st.columns([1.2, 1, 1.2])

# --- טקסט משמאל ---
with left:
    st.markdown(f"""
    <div style="
        direction:rtl;
        text-align:right;
        margin-top:40px;
        color:#1f2a44;
    ">
        <div style="font-size:22px;">
            {greeting}, סיון!
        </div>
        <div style="font-size:13px; color:gray;">
            {date_str}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- תמונה באמצע (בדיוק כמו שהיה) ---
with center:
    st.markdown(f"""
    <div style="
        display:flex;
        justify-content:center;
        margin-top:10px;
    ">
        <div style="
            width:140px;
            height:140px;
            border-radius:50%;
            overflow:hidden;
            border:3px solid #ddd;
            box-shadow:0px 2px 10px rgba(0,0,0,0.15);
        ">
            <img src="data:image/png;base64,{img_base64}" style="
                width:100%;
                height:100%;
                object-fit: cover;
                object-position: center top;
            ">
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- ריק לשמירה על איזון ---
with right:
    st.write("")

st.markdown("---")


# טעינת נתונים
try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except Exception as e:
    st.error(f"שגיאה בטעינת אקסל: {e}")
    st.stop()

# KPI
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='card'><b>פרויקטים</b><br>{len(projects)}</div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='card'><b>בסיכון 🔴</b><br>{len(projects[projects['status']=='אדום'])}</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='card'><b>במעקב 🟡</b><br>{len(projects[projects['status']=='צהוב'])}</div>", unsafe_allow_html=True)

st.markdown("---")

# פרויקטים ולו"ז
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📁 סטטוס פרויקטים")
    for _, row in projects.iterrows():
        st.markdown(f"<div class='card'>{row['project_name']} | {row['status']}</div>", unsafe_allow_html=True)

with col2:
    st.markdown("### 📅 לו״ז להיום")
    t_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
    if not t_meetings.empty:
        for _, r in t_meetings.iterrows():
            st.markdown(f"<div class='card'>📌 {r['meeting_title']} ({r['time']})</div>", unsafe_allow_html=True)
    else:
        st.info("אין פגישות היום")

# ==========================================
# 🤖 אזור ה-AI המעודכן - שדות לבנים, כותרות כרגיל
# ==========================================
st.markdown("---")
st.markdown("<h3 style='text-align:right;'>🤖 עוזר AI אישי</h3>", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    # CSS ממוקד שצובע רק את תיבות הקלט בלבן
    st.markdown("""
        <style>
        /* צביעת הרקע של תיבת הבחירה בלבן */
        div[data-baseweb="select"] > div {
            background-color: white !important;
        }
        /* צביעת הרקע של תיבת הטקסט בלבן */
        .stTextArea textarea {
            background-color: white !important;
        }
        /* יישור לימין לכל אזור הקלט */
        div[data-testid="stSelectbox"], .stTextArea {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        ca1, ca2 = st.columns(2)
        with ca1:
            s_proj = st.selectbox("בחרי פרויקט לניתוח", projects["project_name"].tolist(), key="final_v_2026")
        with ca2:
            u_q = st.text_area("מה תרצי לדעת?", placeholder="למשל: מהם צעדי המניעה לפרויקט באדום?", key="q_2026")

    if st.button("בצע ניתוח AI", key="btn_2026"):
        if u_q:
            p_info = projects[projects["project_name"] == s_proj].iloc[0]
            context = f"נתוני פרויקט: {p_info.to_string()}. ענה בעברית, בנקודות תמציתיות מאוד, ללא כותרות ענק. שאלה: {u_q}"
            
            with st.spinner("מנתח נתונים..."):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {"contents": [{"parts": [{"text": context}]}]}
                
                try:
                    response = requests.post(url, headers=headers, json=data)
                    res_json = response.json()
                    
                    if response.status_code == 200:
                        answer = res_json['candidates'][0]['content']['parts'][0]['text']
                        
                        # תצוגת התשובה בתיבה ירוקה מיושרת לימין
                        st.markdown(f"""
                        <div style="direction: rtl; text-align: right; background-color: #d4edda; color: #155724; 
                                    padding: 15px; border-radius: 10px; border: 1px solid #c3e6cb; 
                                    font-weight: 500; line-height: 1.6; margin-top: 20px;">
                            {answer}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif response.status_code == 429:
                        st.warning("המכסה זמנית הסתיימה. נסי שוב בעוד דקה.")
                    else:
                        st.error(f"שגיאה {response.status_code}")
                except Exception as e:
                    st.error(f"שגיאה בחיבור: {e}")
        else:
            st.warning("נא להזין שאלה.")
else:
    st.error("Missing API Key in Secrets")
