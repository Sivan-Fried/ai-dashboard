import streamlit as st
import pandas as pd
import base64
import os
import datetime
import google.generativeai as genai # שורה 6 התקינה

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
# 🤖 AI AREA - מותאם לספריה היציבה
# ==========================================
st.markdown("---")
st.markdown("### 🤖 עוזר AI")

api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    # אתחול ה-AI בשיטה הישנה והטובה
    genai.configure(api_key=api_key)
    
    ca1, ca2 = st.columns(2)
    with ca1:
        s_proj = st.selectbox("בחרי פרויקט", projects["project_name"].tolist(), key="final_v1")
    with ca2:
        u_q = st.text_area("שאלה", key="final_v2")

 if st.button("בצע ניתוח", key="final_v3"):
        if u_q:
            p_info = projects[projects["project_name"] == s_proj].iloc[0]
            prompt = f"פרויקט: {p_info['project_name']}, סטטוס: {p_info['status']}. שאלה: {u_q}"
            with st.spinner("מנתח..."):
                try:
                    # התיקון כאן: הסרנו את הקידומת models/ והשארנו רק gemini-1.5-flash
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    res = model.generate_content(prompt)
                    st.success(res.text)
                except Exception as e:
                    st.error(f"שגיאה בניתוח: {e}")
        else:
            st.warning("נא להזין שאלה.")
else:
    st.error("Missing API Key in Secrets")
