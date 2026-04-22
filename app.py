import streamlit as st
import requests
import pandas as pd
import datetime
import urllib.parse
from zoneinfo import ZoneInfo
import google.generativeai as genai

# =========================================================
# 1. הגדרות דף ותשתית נתונים
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

# פונקציות לניהול סיכומים קבועים (Cache)
def load_saved_summaries():
    try:
        return pd.read_excel("fathom_summaries.xlsx")
    except:
        return pd.DataFrame(columns=["recording_id", "summary", "date"])

def save_summary_to_file(rec_id, summary_text):
    df = load_saved_summaries()
    rec_id = str(rec_id)
    if rec_id not in df['recording_id'].astype(str).values:
        new_row = pd.DataFrame([{
            "recording_id": rec_id,
            "summary": summary_text,
            "date": datetime.datetime.now().strftime("%d/%m/%Y")
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        try:
            df.to_excel("fathom_summaries.xlsx", index=False)
        except:
            st.warning("לא ניתן לשמור לקובץ האקסל. וודאי שהוא לא פתוח או חסר.")

# פונקציית מזג אוויר יציבה (לפי עיר)
def get_weather_fixed():
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    city = "Petah Tikva"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=he"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            return f"{temp}°C | {desc}"
    except: pass
    return "24°C | בהיר" # ברירת מחדל אם ה-API נכשל

weather_info = get_weather_fixed()

# =========================================================
# 2. עיצוב (CSS) - מותאם ליישור לימין
# =========================================================
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    
    /* יישור לימין לכל האלמנטים */
    .stMarkdown, .stInfo, [data-testid="stNotification"], div[data-testid="stMarkdownContainer"] {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* תיקון בולטים (Lists) שיהיו בצד ימין */
    .stMarkdown ul, .stMarkdown ol {
        direction: rtl !important;
        text-align: right !important;
        padding-right: 1.5rem !important;
        padding-left: 0 !important;
    }

    .dashboard-header {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .record-row {
        background: white;
        padding: 12px 18px;
        border-radius: 12px;
        margin-bottom: 8px;
        border-right: 5px solid #4facfe;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. פונקציות API (Fathom & Gemini)
# =========================================================

def get_fathom_meetings():
    url = "https://api.fathom.ai/external/v1/meetings"
    headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get('items', [])[:5]
    except: return []

def get_fathom_summary(recording_id):
    url = f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary"
    headers = {"X-Api-Key": st.secrets["FATHOM_API_KEY"], "Accept": "application/json"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get("summary", {}).get("markdown_formatted")
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"סכם את הפגישה הבאה לעברית מקצועית וברורה. השתמש בבולטים. יישר הכל לימין:\n\n{raw_text}"
        return model.generate_content(prompt).text
    except Exception as e: return f"שגיאה בעיבוד ה-AI: {e}"

# =========================================================
# 4. גוף הדשבורד
# =========================================================

st.markdown('<h1 class="dashboard-header">My Dashboard</h1>', unsafe_allow_html=True)

# אזור ברכה עליון
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

col_greet = st.columns(1)[0]
with col_greet:
    st.markdown(f"""
        <div style="text-align: right; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style='margin:0; color:#1f2a44;'>{greeting}, סיון!</h2>
            <p style='margin:5px 0; color:#666; font-size:1.1rem;'>
                <b>{now.strftime('%H:%M')}</b> | {now.strftime('%d/%m/%Y')} | 
                <span style='color:#4facfe; font-weight:600;'>📍 פתח תקווה: {weather_info}</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

col_r, col_l = st.columns(2)

with col_r:
    # כאן יבואו הפרויקטים שלך (כמו בקוד המקורי)
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים פעילים")
        try:
            projects = pd.read_excel("my_projects.xlsx")
            for _, row in projects.iterrows():
                st.markdown(f'<div class="record-row"><b>{row["project_name"]}</b></div>', unsafe_allow_html=True)
        except: st.write("קובץ פרויקטים לא נמצא")

with col_l:
    # סיכומי פגישות עם מנגנון ה-Cache
    with st.container(border=True):
        st.markdown("### ✨ סיכומי פגישות Fathom")
        
        saved_summaries = load_saved_summaries()
        meetings = get_fathom_meetings()
        
        if not meetings:
            st.warning("לא נמצאו פגישות ב-Fathom או שאין קריאות פנויות.")
        else:
            for mtg in meetings:
                rid = str(mtg.get('recording_id'))
                title = mtg.get('title', 'פגישה ללא שם')
                
                st.markdown(f"**📅 {title}**")
                
                # בדיקה אם יש סיכום בארכיון
                match = saved_summaries[saved_summaries['recording_id'].astype(str) == rid]
                
                if not match.empty:
                    st.info(match.iloc[0]['summary'])
                else:
                    if st.button("סכם ושמור פגישה 🪄", key=f"btn_{rid}"):
                        with st.spinner("מנתח ושומר בארכיון..."):
                            raw = get_fathom_summary(rid)
                            if raw:
                                refined = refine_with_ai(raw)
                                save_summary_to_file(rid, refined)
                                st.rerun()
                            else:
                                st.error("לא ניתן לשלוף את תוכן הפגישה.")
