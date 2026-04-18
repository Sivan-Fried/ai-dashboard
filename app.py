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



# =========================
# נתונים
# =========================
projects = pd.read_excel("my_projects.xlsx")
meetings = pd.read_excel("meetings.xlsx")
reminders = pd.read_excel("reminders.xlsx")

today = pd.Timestamp.today().date()

# =========================
# AI תזכורות
# =========================
def generate_ai_reminders(df):
    ai = []
    for _, row in df.iterrows():
        if row["status"] in ["צהוב", "אדום"]:
            ai.append({
                "reminder_text": f"התחלה/מעקב על {row['project_name']}",
                "project_name": row["project_name"],
                "date": today,
                "priority": "medium",
                "source": "ai"
            })
    return pd.DataFrame(ai)

ai_reminders = generate_ai_reminders(projects)

if "reminders_live" not in st.session_state:
    st.session_state.reminders_live = pd.concat([reminders, ai_reminders], ignore_index=True)

# =========================
# KPI
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"<div class='card'><b>סה״כ פרויקטים</b><br>{len(projects)}</div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"<div class='card'><b>בסיכון 🔴</b><br>{len(projects[projects['status']=='אדום'])}</div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"<div class='card'><b>במעקב 🟡</b><br>{len(projects[projects['status']=='צהוב'])}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# פרויקטים
# =========================
st.markdown(
    "<h3 style='text-align:right; direction:rtl;'>📁 פרויקטים</h3>",
    unsafe_allow_html=True
)

def type_icon(project_type):
    if project_type == "פרויקט אקטיבי":
        return "🚀"
    elif project_type == "חבילת עבודה":
        return "📦"
    elif project_type == "תחזוקה":
        return "🔧"
    else:
        return "📁"

def status_dot(status):
    if status == "ירוק":
        return "🟢"
    elif status == "צהוב":
        return "🟡"
    else:
        return "🔴"

for _, row in projects.iterrows():

    project_name = row["project_name"]
    project_type = row["project_type"]
    status = row["status"]

    icon = type_icon(project_type)
    dot = status_dot(status)

    st.markdown(f"""
    <div style="
        background:white;
        padding:8px 10px;
        border-radius:8px;
        margin-bottom:4px;
        border:1px solid #eee;
        direction:rtl;
        text-align:right;
        font-size:14px;
    ">
        {icon} {project_name}
        <span style="color:gray; font-size:12px;"> | {project_type}</span>
        <span style="float:left;">{dot}</span>
    </div>
    """, unsafe_allow_html=True)
    
# --- ריק לשמירה על איזון ---
with right:
    st.write("")

st.markdown("---")

# =========================
# 🔥 חשוב – הגדרת עמודות (לא לגעת!)
# =========================
col_right, col_left = st.columns(2)

# -------- פגישות --------
with col_right:

    st.markdown("### 📅 פגישות היום")

    today_meetings = meetings[pd.to_datetime(meetings["date"]).dt.date == today]

    if today_meetings.empty:
        st.info("אין פגישות היום 🎉")
    else:
        for _, row in today_meetings.iterrows():
            st.markdown(f"""
            <div class='card'>
                📌 {row['meeting_title']}<br>
                🕒 {row['time']}<br>
                📁 {row['project_name']}
            </div>
            """, unsafe_allow_html=True)

# -------- תזכורות --------
with col_left:

    st.markdown("### 🔔 תזכורות")

    today_reminders = st.session_state.reminders_live[
        pd.to_datetime(st.session_state.reminders_live["date"]).dt.date == today
    ]

    # 🔥 גלילה אמיתית
    container = st.container(height=260)

    with container:

        if today_reminders.empty:
            st.info("אין תזכורות להיום 🎉")

        else:
            for _, row in today_reminders.iterrows():

                icon = "🤖" if row["source"] == "ai" else "✍️"

                st.markdown(f"""
                <div class="card">
                    {icon} {row['reminder_text']} | 📁 {row['project_name']}
                </div>
                """, unsafe_allow_html=True)

    # =========================
    # ➕ הוספה
    # =========================
    st.markdown("---")

    if "add_mode" not in st.session_state:
        st.session_state.add_mode = False

    if not st.session_state.add_mode:

        if st.button("➕ הוספת תזכורת"):
            st.session_state.add_mode = True
            st.rerun()

    else:

        col1, col2, col3, col4 = st.columns([5, 3, 2, 1])

        with col1:
            text = st.text_input("", placeholder="תזכורת חדשה")

        with col2:
            project = st.selectbox("", projects["project_name"].tolist())

        with col3:
            priority = st.selectbox("", ["נמוכה", "בינונית", "גבוהה"])

        with col4:
            if st.button("✔"):

                reverse = {"נמוכה":"low","בינונית":"medium","גבוהה":"high"}

                new_row = {
                    "reminder_text": text,
                    "project_name": project,
                    "date": today,
                    "priority": reverse[priority],
                    "source": "manual"
                }

                st.session_state.reminders_live.loc[len(st.session_state.reminders_live)] = new_row

                st.session_state.add_mode = False
                st.rerun()

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
