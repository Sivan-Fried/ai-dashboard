import streamlit as st
import pandas as pd
import requests
import json
import base64
import os
import datetime

# הגדרת עמוד
st.set_page_config(layout="wide", page_title="AI Dashboard")

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

# פרופיל
def get_base64_img(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""
    return ""

img_b64 = get_base64_img("profile.png")
date_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

col_l, col_c, col_r = st.columns([1,1,1])
with col_l:
    st.markdown(f"<div style='direction:rtl;text-align:right;margin-top:30px;'><b>שלום סיון!</b><br>{date_str}</div>", unsafe_allow_html=True)
with col_c:
    if img_b64:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_b64}" style="width:120px;height:120px;border-radius:50%;border:3px solid #ddd;"></div>', unsafe_allow_html=True)

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
    else: st.info("אין פגישות היום")

# ==========================================
# 🤖 AI AREA - THE FINAL FIX
# ==========================================
st.markdown("---")
st.markdown("### 🤖 עוזר AI")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    ca1, ca2 = st.columns(2)
    with ca1:
        s_proj = st.selectbox("בחרי פרויקט", projects["project_name"].tolist(), key="v_final")
    with ca2:
        u_q = st.text_area("שאלה", key="q_final")

    if st.button("בצע ניתוח"):
        if u_q:
            p_info = projects[projects["project_name"] == s_proj].iloc[0]
            context = f"Project: {p_info['project_name']}, Status: {p_info['status']}. Question: {u_q}"
            
            with st.spinner("מנתח..."):
                # שימוש במודל gemini-1.0-pro - הכי נפוץ והכי פחות עושה בעיות 404
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {"contents": [{"parts": [{"text": context}]}]}
                
                try:
                    response = requests.post(url, headers=headers, json=data)
                    res_json = response.json()
                    
                    if response.status_code == 200:
                        answer = res_json['candidates'][0]['content']['parts'][0]['text']
                        st.success(answer)
                    else:
                        st.error(f"שגיאה (404): המודל לא נמצא. זה קורה בדרך כלל בגלל הגבלות אזור של ה-API Key.")
                        st.info("נסי ליצור API Key חדש לגמרי תחת פרויקט חדש ב-Google AI Studio.")
                except Exception as e:
                    st.error(f"שגיאה טכנית: {e}")
else:
    st.error("Missing API Key in Secrets")
