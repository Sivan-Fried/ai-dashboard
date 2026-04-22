import streamlit as st
import requests
import pandas as pd
import datetime
from zoneinfo import ZoneInfo
import google.generativeai as genai

# ==========================================
# 1. הגדרות וחיבורים (Secrets)
# ==========================================
st.set_page_config(layout="wide", page_title="Sivan Dashboard")

# פונקציה לשליפת מזג אוויר (לפי עיר - הכי יציב)
def get_weather():
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    if not api_key: return "חסר מפתח API"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Petah Tikva&appid={api_key}&units=metric&lang=he"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            return f"{temp}°C | {desc}"
    except: pass
    return "מידע לא זמין"

# פונקציות לניהול הארכיון (Cache באקסל)
def load_archive():
    try: return pd.read_excel("fathom_summaries.xlsx")
    except: return pd.DataFrame(columns=["recording_id", "summary", "date"])

def save_to_archive(rid, summary):
    df = load_archive()
    if str(rid) not in df['recording_id'].astype(str).values:
        new_data = pd.DataFrame([{"recording_id": str(rid), "summary": summary, "date": datetime.date.today()}])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel("fathom_summaries.xlsx", index=False)

# ==========================================
# 2. עיצוב וסגנון (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; direction: rtl; }
    .header-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-right: 10px solid #4facfe;
        text-align: right;
        margin-bottom: 30px;
    }
    .weather-tag {
        background: #f0f9ff;
        color: #0369a1;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. תצוגת ראש הדף (ברכה ומזג אוויר)
# ==========================================
now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"
weather_display = get_weather()

st.markdown(f"""
<div class="header-container">
    <h1 style='margin:0;'>{greeting}, סיון! 👋</h1>
    <p style='margin:5px 0; font-size:1.1rem; color:#64748b;'>
        {now.strftime('%H:%M')} | {now.strftime('%d/%m/%Y')}
    </p>
    <div class="weather-tag">📍 פתח תקווה: {weather_display}</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. תוכן הדשבורד (פרויקטים וסיכומים)
# ==========================================
col_r, col_l = st.columns(2)

with col_r:
    st.subheader("📁 הפרויקטים שלי")
    try:
        df_proj = pd.read_excel("my_projects.xlsx")
        st.dataframe(df_proj, use_container_width=True, hide_index=True)
    except:
        st.info("מעלה נתוני פרויקטים...")

with col_l:
    st.subheader("✨ סיכומי פגישות (Fathom)")
    
    # טעינת ארכיון ונתונים מה-API
    archive = load_archive()
    
    # כאן צריכה לבוא פונקציית get_fathom_meetings שלך
    # נניח שזו התוצאה:
    mock_meetings = [{"recording_id": "123", "title": "פגישת אפיון דשבורד"}] 
    
    for mtg in mock_meetings:
        rid = str(mtg['recording_id'])
        st.write(f"**{mtg['title']}**")
        
        # בדקי בארכיון
        match = archive[archive['recording_id'].astype(str) == rid]
        if not match.empty:
            st.info(match.iloc[0]['summary'])
        else:
            if st.button("סכם ושמור בארכיון", key=rid):
                # כאן תבוא לוגיקת ה-Gemini שלך
                summary = "סיכום AI לדוגמה..." 
                save_to_archive(rid, summary)
                st.rerun()
