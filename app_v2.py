# -*- coding: utf-8 -*-

# =========================================================
# ייבוא ספריות
# =========================================================
import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import urllib.parse
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components
import google.generativeai as genai
from streamlit_js_eval import get_geolocation
from workplan_module import build_timeline_html
from urllib.parse import urlencode

# הגדרות דף
st.set_page_config(
    layout="wide",
    page_title="Dashboard Sivan",
    initial_sidebar_state="collapsed"
)

# 1. שחרור חסימות גובה (התיקון הקריטי)
# הסבר: הקוד הזה אומר ל-Streamlit לא לחתוך אלמנטים שיוצאים מהגבולות שלהם (overflow: visible)
st.markdown("""
<style>
    /* מאפשר לכל רכיב iframe בדף להציג תוכן מחוץ לגבולות התיבה שלו */
    iframe {
        overflow: visible !important;
    }
    /* מונע מהמיכלים של סטרימליט (עמודות ושורות) לחתוך את התפריט הנפתח */
    [data-testid="stVerticalBlock"], 
    [data-testid="stHorizontalBlock"], 
    .element-container {
        overflow: visible !important;
    }
</style>
""", unsafe_allow_html=True)

# טעינת פונטים — Material Symbols Rounded לאייקונים, Plus Jakarta Sans לטקסט
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" />', unsafe_allow_html=True)

# טעינת קובץ העיצוב החיצוני — styles_v2.css
with open("styles_v2.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ai-card עיצוב כרטיס ה-AI
st.markdown("""
<style>
.ai-box {
    background-color: #FADCE6;
    padding: 24px;
    border-radius: 24px;
    box-shadow: 0px 10px 30px rgba(225,200,210,0.25);
    direction: rtl;
    margin-bottom: 20px;
}
.ai-title {
    font-size: 20px;
    font-weight: 600;
    color: #6f5861;
    margin: 0;
}
.ai-desc {
    font-size: 14px;
    color: #6f5861;
    opacity: 0.85;
    margin-bottom: 16px;
}
/* כפתור השליחה הצף בתוך הכרטיס */
.ai-send {
    background-color: #6f5861;
    color: white;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-top: -50px;
    margin-right: 10px;
    float: left;
}
</style>
""", unsafe_allow_html=True)


    
# --- כאן מתחיל התוכן של הדשבורד הישן שלך ---
# =========================================================
# =========================================================
# סרגל עליון + פעמון נוטיפיקציות — גרסה מתוקנת (ללא חיתוך)
# =========================================================
# =========================================================
# פעמון נוטיפיקציות — חלונית צפה אמיתית (JS)
# =========================================================
# =========================================================
# טעינת נתונים
# =========================================================
try:
    projects     = pd.read_excel("my_projects.xlsx")
    meetings     = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    priority_df  = pd.read_excel("priority.xlsx")
except Exception as e:
    st.error(f"שגיאה בטעינת קבצים: {e}"); st.stop()

today = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).date()
def render_topbar_with_bell(img_b64, w_text, w_city, greeting, today_reminders):
    import re
    import datetime
    from zoneinfo import ZoneInfo
    import streamlit.components.v1 as components
    
    # הגדרות זמן ותאריך
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%d/%m/%Y")

    # ניקוי טקסט מזג אוויר ותווים מיוחדים
    w_text_clean = re.sub(r'[^\x00-\x7F]+', '', w_text).strip().replace('C', '\u00b0C')
    profile_src = f"data:image/png;base64,{img_b64}" if img_b64 else ""
    
    # חישוב כמות הודעות שלא נקראו לבאדג'
    if 'is_read' in today_reminders.columns:
        unread_count = len(today_reminders[today_reminders['is_read'] == False])
    else:
        unread_count = len(today_reminders)
    
    badge_display = 'flex' if unread_count > 0 else 'none'

    # בניית רשימת התראות עם טיפול בתווים מיוחדים
    items_html = ""
    if today_reminders.empty:
        items_html = '<div class="sn-empty">אין תזכורות להיום 🎉</div>'
    else:
        for _, row in today_reminders.iterrows():
            text = str(row.get("reminder_text", "")).replace('"', '&quot;').replace("'", "&#39;").replace("<", "&lt;").replace(">", "&gt;")
            proj = str(row.get("project_name", "כללי")).replace('"', '&quot;').replace("'", "&#39;")
            
            is_read = row.get("is_read", False)
            read_class = "read" if is_read else "unread"
            
            items_html += f"""
            <div class="sn-item {read_class}" onclick="this.classList.add('read'); updateBadge();">
                <div class="sn-dot"></div>
                <div style="flex:1;">
                    <div class="sn-text">{text}</div>
                    <div class="sn-proj">{proj}</div>
                </div>
            </div>"""

    items_js = items_html.replace('`', r'\`').replace('\\', '\\\\').replace('\n', '')

    components.html(f"""<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="utf-8"/>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    background: transparent !important; 
    overflow: hidden; 
    height: 110px; 
    direction: rtl; 
  }}
  
  .topbar {{ 
    background: white; 
    border-radius: 16px; 
    border: 1px solid #F4F4F5;
    box-shadow: 0 2px 20px rgba(225,200,210,0.2); 
    display: flex;
    align-items: center; 
    justify-content: space-between; 
    padding: 0 24px;
    height: 100px; 
    position: relative; 
    z-index: 100;
  }}

  /* צד ימין */
  .tb-right {{ display:flex; align-items:center; gap:16px; }}
  .tb-profile {{ width:72px; height:72px; border-radius:50%; object-fit:cover; border:3px solid white; box-shadow:0 2px 12px rgba(225,200,210,0.4); }}
  .tb-name {{ font-size:0.95rem; font-weight:700; color:#3f3f46; }}
  .tb-role {{ font-size:0.75rem; color:#a1a1aa; }}

  /* ניווט מרכזי */
  .tb-nav {{ display:flex; gap:4px; flex:1; justify-content:center; }}
  .tb-nav span {{ 
    font-size:0.82rem; 
    padding:8px 16px; 
    border-radius:20px; 
    color:#71717A; 
    cursor:pointer; 
    transition: all 0.2s ease;
  }}
  .tb-nav span:hover {{ background: #FDF2F7; color: #3f3f46; }}
  .tb-nav span.active {{ background:#FADCE6; color:#3f3f46; font-weight:600; }}

  /* צד שמאל */
  .tb-left {{ display:flex; align-items:center; gap:16px; }}
  .tb-divider {{ width:1px; height:28px; background:#F4F4F5; flex-shrink:0; }}
  .weather-wrap {{ display: flex; align-items: center; gap: 8px; text-align: right; }}
  .time-wrap {{ text-align: right; min-width: 75px; }}
  
  /* פעמון */
  .bell-area {{ position:relative; cursor:pointer; display:flex; align-items:center; justify-content:center; width:40px; height:40px; border-radius:50%; transition: background 0.2s; }}
  .bell-area:hover {{ background: #FDF2F7; }}
  .bell-badge {{ 
    position:absolute; top:2px; left:2px; background:#ef4444; color:white;
    border-radius:50%; min-width:18px; height:18px; font-size:0.62rem;
    display:{badge_display}; align-items:center; justify-content:center; border:2px solid white; font-weight:bold;
  }}
</style>
</head>
<body>
<div class="topbar">
  <div class="tb-right">
    <img class="tb-profile" src="{profile_src}"/>
    <div>
        <div class="tb-name">{greeting}, סיון</div>
        <div class="tb-role">מנהלת פרויקטים</div>
    </div>
    <div class="bell-area" id="bellBtn">
      <span class="bell-badge" id="badge">{unread_count}</span>
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#71717A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8C18 6.4087 17.3679 4.88258 16.2426 3.75736C15.1174 2.63214 13.5913 2 12 2C10.4087 2 8.88258 2.63214 7.75736 3.75736C6.63214 4.88258 6 6.4087 6 8C6 15 3 17 3 17H21C21 17 18 15 18 8Z"></path>
        <path d="M13.73 21C13.5542 21.3031 12 21.9965 10.27 21"></path>
      </svg>
    </div>
  </div>

  <nav class="tb-nav">
    <span class="active">דשבורד</span>
    <span>פרויקטים</span>
    <span>פגישות</span>
    <span>משימות</span>
    <span>דוחות</span>
  </nav>

  <div class="tb-left">
    <div class="weather-wrap">
      <div style="color:#f0b8cb;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"></path>
        </svg>
      </div>
      <div>
        <div style="font-size:0.82rem; font-weight:600; color:#3f3f46;">{w_text_clean}</div>
        <div style="font-size:0.68rem; color:#a1a1aa;">{w_city}</div>
      </div>
    </div>
    <div class="tb-divider"></div>
    <div class="time-wrap">
      <div style="font-size:0.85rem; font-weight:700; color:#3f3f46;">{time_str}</div>
      <div style="font-size:0.68rem; color:#a1a1aa;">{date_str}</div>
    </div>
    <div class="tb-divider"></div>
    <div style="font-size:0.95rem; font-weight:800; color:#f0b8cb;">Dashboard AI</div>
  </div>
</div>

<script>
  var isOpen = false;
  
  function updateBadge() {{
    var parentDoc = window.parent.document;
    var d = parentDoc.getElementById('sn-floating-dropdown');
    var unreadCount = d.querySelectorAll('.sn-item:not(.read)').length;
    var badge = document.getElementById('badge');
    if (unreadCount === 0) badge.style.display = 'none';
    else {{ badge.style.display = 'flex'; badge.textContent = unreadCount; }}
  }}

  window.addEventListener('load', function() {{
    var parentDoc = window.parent.document;
    
    var old = parentDoc.getElementById('sn-floating-dropdown'); if (old) old.remove();
    var oldStyle = parentDoc.getElementById('sn-styles'); if (oldStyle) oldStyle.remove();

    var style = parentDoc.createElement('style');
    style.id = 'sn-styles';
    style.textContent = `
      #sn-floating-dropdown {{
        display:none; position:fixed; width:360px; background:white;
        border-radius:20px; box-shadow:0 10px 40px rgba(0,0,0,0.15);
        border:1px solid #fdf0f5; z-index:1000000; overflow-y:auto; max-height:450px;
        direction:rtl; font-family: sans-serif;
      }}
      .sn-header {{ padding:16px 20px; font-weight:700; border-bottom:1px solid #fdf0f5; color:#3f3f46; }}
      .sn-item {{ padding:14px 20px; display:flex; align-items:center; gap:14px; cursor:pointer; border-bottom:1px solid #fdf6f9; transition:0.15s; }}
      .sn-item:hover {{ background:#fdf6f9; }}
      .sn-item.read {{ opacity: 0.5; }}
      .sn-item.read .sn-dot {{ background:#cbd5e1 !important; }}
      .sn-dot {{ width:8px; height:8px; border-radius:50%; background:#FADCE6; flex-shrink:0; }}
      .sn-text {{ font-size:0.85rem; color:#3f3f46; font-weight:500; line-height:1.4; }}
      .sn-proj {{ font-size:0.72rem; color:#a1a1aa; margin-top:2px; }}
    `;
    parentDoc.head.appendChild(style);

    var dropdown = parentDoc.createElement('div');
    dropdown.id = 'sn-floating-dropdown';
    dropdown.innerHTML = '<div class="sn-header">התראות להיום</div>' + `{items_js}`;
    parentDoc.body.appendChild(dropdown);

    parentDoc.addEventListener('scroll', function() {{
      var d = parentDoc.getElementById('sn-floating-dropdown');
      if (d && d.style.display === 'block') {{
        var iframe = window.frameElement;
        var rect = iframe.getBoundingClientRect();
        d.style.top = (rect.bottom + 8) + 'px';
      }}
    }}, true);

    parentDoc.addEventListener('click', function(e) {{
      var d = parentDoc.getElementById('sn-floating-dropdown');
      if (isOpen && d && !d.contains(e.target)) {{ d.style.display = 'none'; isOpen = false; }}
    }}, true);
  }});

  document.getElementById('bellBtn').addEventListener('click', function(e) {{
    var parentDoc = window.parent.document;
    var d = parentDoc.getElementById('sn-floating-dropdown');
    isOpen = !isOpen;
    if (isOpen) {{
      var iframe = window.frameElement;
      var rect = iframe.getBoundingClientRect();
      var bellRect = this.getBoundingClientRect();
      d.style.top = (rect.bottom + 8) + 'px';
      d.style.left = (rect.left + bellRect.left - 300) + 'px';
      d.style.display = 'block';
    }} else {{ d.style.display = 'none'; }}
    e.stopPropagation();
  }});
</script>
</body>
</html>""", height=110)
#סוף נסיון


# ---תמונת פרופיל ---
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# =========================================================
# 2. פונקציות עזר ונתונים
# =========================================================

def get_weather_realtime(location):
    if location and 'coords' in location:
        lat, lon = location['coords']['latitude'], location['coords']['longitude']
        try:
            g = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}", headers={'User-Agent': 'SivanDash'}).json()
            city = g.get('address', {}).get('city') or g.get('address', {}).get('town') or "ישראל"
            w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
            temp = round(w['current_weather']['temperature'])
            hour = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).hour
            icon = "🌙" if (hour >= 19 or hour < 6) else "☀️"
            return f"{icon} {temp}°C", city
        except: pass
    return "☀️ --°C", "ישראל"

def get_azure_tasks():
    ORG_NAME = "amandigital"
    wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject], [System.CreatedDate] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids: return []
        details = requests.get(f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject,System.CreatedDate&api-version=6.0", auth=auth)
        return details.json().get('value', [])
    except: return []

def get_fathom_meetings():
    api_key = st.secrets["FATHOM_API_KEY"]
    url = "https://api.fathom.ai/external/v1/meetings"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200: return response.json().get('items', [])[:5], 200
        return [], response.status_code
    except: return [], 500

def get_fathom_summary(recording_id):
    api_key = st.secrets["FATHOM_API_KEY"]
    url = f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200: return response.json().get("summary", {}).get("markdown_formatted")
        return None
    except: return None

def refine_with_ai(raw_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        prompt = f"""סכם את הפגישה לעברית עסקית רהוטה.
השתמש בפורמט Markdown: כותרות עם ##, בולטים עם -, מספור עם 1. 2. 3.

{raw_text}"""
        return model.generate_content(prompt).text
    except Exception as e:
        return f"שגיאה בסיכום: {str(e)}"

def fmt_time(t):
    try: return t.strftime("%H:%M")
    except: return ""

def save_summary_to_excel(title, date_str, summary_text):
    file_path = "fathom_summaries.xlsx"
    new_row = {
        "title": title, "date": date_str, "summary": summary_text,
        "created_at": datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d/%m/%Y %H:%M")
    }
    try:
        existing = pd.read_excel(file_path)
        if "title" not in existing.columns:
            updated = pd.DataFrame([new_row])
        elif title in existing["title"].values:
            return
        else:
            updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
    except FileNotFoundError:
        updated = pd.DataFrame([new_row])
    updated.to_excel(file_path, index=False)

# =========================================================
# פעמון נוטיפיקציות — חלונית צפה אמיתית (JS)
# =========================================================
# =========================================================
# טעינת נתונים
# =========================================================
try:
    projects     = pd.read_excel("my_projects.xlsx")
    meetings     = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    priority_df  = pd.read_excel("priority.xlsx")
except Exception as e:
    st.error(f"שגיאה בטעינת קבצים: {e}"); st.stop()

today = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).date()

# =========================================================
# 3. ניהול ניווט ו-Session State
# =========================================================
if "current_page"    not in st.session_state: st.session_state.current_page    = "main"
if "rem_live"        not in st.session_state: st.session_state.rem_live        = reminders_df
if "ai_response"     not in st.session_state: st.session_state.ai_response     = ""
if "adding_reminder" not in st.session_state: st.session_state.adding_reminder = False

params = st.query_params
if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

# =========================================================
# 4. מבנה התצוגה
# =========================================================
loc = get_geolocation()

if st.session_state.current_page == "project":
    p_name = st.session_state.get("selected_project", "פרויקט")
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)
    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear()
        st.session_state.current_page = "main"
        st.rerun()
        
    with st.container(border=True):
        st.markdown(f"### ℹ️ ניהול פרויקט: {p_name}")
        tab_work, tab_res, tab_risk, tab_meetings = st.tabs(["📅 תוכנית עבודה", "👥 משאבים", "⚠️ סיכונים", "📝 סיכומים"])
        with tab_work:
            try:
                html = build_timeline_html(p_name)
                st.components.v1.html(html, height=300, scrolling=False)
            except Exception as e:
                st.error(f"שגיאה בטעינת תוכנית העבודה: {e}")

        with tab_res:      st.write("רשימת צוות ומשאבים")
        with tab_risk:     st.write("ניהול סיכונים")
        with tab_meetings: st.write("סיכומי פגישות הפרויקט")

else:
    # ── מזג אוויר ──────────────────────────────────────────
    if loc:
        w_text, w_city = get_weather_realtime(loc)
    else:
        w_text, w_city = "☀️ --°C", "מזהה מיקום..."

    
    # ── אזור פרופיל + סרגל עליון ───────────────────────────
    img_b64  = get_base64_image("profile.png")
    now      = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = "בוקר טוב" if 5 <= now.hour < 12 else "צהריים טובים" if 12 <= now.hour < 18 else "ערב טוב"

    # ⭐ סרגל עליון + פעמון משולבים ⭐
    # 1. סינון ההתראות להיום
    today_reminders = st.session_state.rem_live[
        pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today
    ].copy() # הוספנו copy כדי שנוכל לשנות את העמודה בביטחון
    
    # 2. התיקון הקריטי: מוודאים שיש עמודה בשם is_read שהפונקציה מכירה
    # אם יש לך עמודה בשם status או read_status, תשני את השם 'status' למטה למה שיש לך
    if 'status' in today_reminders.columns:
        today_reminders['is_read'] = today_reminders['status'].apply(lambda x: x in [True, 1, 'read'])
    elif 'is_read' not in today_reminders.columns:
        # אם בכלל אין עמודה כזו, ניצור אחת כברירת מחדל (הכל לא נקרא)
        today_reminders['is_read'] = False
    
    # 3. קריאה לפונקציה
    render_topbar_with_bell(img_b64, w_text, w_city, greeting, today_reminders)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Daily Quote Section Logic & Display ──────────────────────────
    # ── Quote Section Display Logic ───────────────────────────────
    import pandas as pd
    import random
    import os
    
    # ודאי שהקובץ inspirational_quotes.xlsx נמצא בתיקיית הפרויקט
    file_path = "inspirational_quotes.xlsx"
    
    # ברירת מחדל למקרה של תקלה בטעינת הקובץ
    quote_text = "המסע היחיד הוא זה שבפנים."
    quote_author = "לא ידוע"
    
    # מנגנון טעינה בטוח
    if os.path.exists(file_path):
        try:
            quotes_df = pd.read_excel(file_path, engine='openpyxl')
            if not quotes_df.empty:
                # בחירת שורה רנדומלית
                random_row = quotes_df.sample(n=1).iloc[0]
                
                # וידוא ששמות העמודות באקסל תואמים בדיוק: quote ו-author
                quote_text = str(random_row.get('quote', quote_text))
                quote_author = str(random_row.get('author', quote_author))
        except Exception as e:
            # הדפסה ללוגים בלבד במקרה של שגיאה בטעינת הקובץ
            print(f"Error loading inspirational quotes: {e}")
    
    # ── ה-HTML המעודכן, נקי מכפילויות ועם הפרדה ברורה ─────────────────
    # שימי לב: אין כאן כפילויות, רק מבנה אחד נקי ומסודר.
    quote_content = f"""
    <div class="quote-wrapper-outer">
        <div class="watercolor-shape">
            <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                <path d="M44.7,-76.4C58.1,-69.2,69.2,-58.1,76.4,-44.7C83.7,-31.4,87,-15.7,86.2,-0.4C85.4,14.8,80.5,29.7,72,42.9C63.5,56.1,51.4,67.7,37.3,74.5C23.2,81.4,7,83.4,-8.8,81.9C-24.6,80.4,-40,75.4,-53.4,66.6C-66.8,57.8,-78.2,45.2,-83.4,30.6C-88.6,16,-87.6,-0.6,-83.1,-15.8C-78.6,-31,-70.7,-44.8,-59.6,-53.6C-48.5,-62.4,-34.2,-66.2,-20.5,-73C-6.8,-79.8,6.3,-89.6,20.5,-89.6C34.7,-89.6,44.7,-76.4Z" transform="translate(100 100)"></path>
            </svg>
        </div>
        
        <div class="quote-content-flat">
            <span class="quote-label">Daily Quote</span>
            
            <div class="quote-main-text">"{quote_text}"</div>
            
            <div class="quote-author-row">
                <span>{quote_author}</span>
                <div class="author-line"></div>
            </div>
            
            <div class="bottom-ornament">
                <div class="ornament-line"></div>
                <span class="material-symbols-rounded">auto_stories</span>
                <div class="ornament-line"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(quote_content, unsafe_allow_html=True)
            
    
    # ── KPIs ────────────────────────────────────────────────
    # ── KPIs New Compact Design ───────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        val = len(projects[projects["status"]=="אדום"])
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fef2f2;"><span class="material-symbols-rounded" style="color:#f87171;">warning</span></div>
                <span class="kpi-badge" style="background:#fef2f2; color:#ef4444;">בסיכון</span>
            </div>
            <div class="kpi-content">
                <div class="kpi-value-row">
                    <span class="kpi-unit">פרויקטים</span>
                    <span class="kpi-number">{val}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with k2:
        val = len(projects[projects["status"]=="צהוב"])
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#eff6ff;"><span class="material-symbols-rounded" style="color:#60a5fa;">info</span></div>
                <span class="kpi-badge" style="background:#eff6ff; color:#3b82f6;">במעקב</span>
            </div>
            <div class="kpi-content">
                <div class="kpi-value-row">
                    <span class="kpi-unit">פרויקטים</span>
                    <span class="kpi-number">{val}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with k3:
        val = len(projects[projects["status"]=="ירוק"])
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#ecfdf5;"><span class="material-symbols-rounded" style="color:#34d399;">check_circle</span></div>
                <span class="kpi-badge" style="background:#ecfdf5; color:#10b981;">תקין</span>
            </div>
            <div class="kpi-content">
                <div class="kpi-value-row">
                    <span class="kpi-unit">פרויקטים</span>
                    <span class="kpi-number">{val}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with k4:
        val = len(projects)
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#f8fafc;"><span class="material-symbols-rounded" style="color:#94a3b8;">folder</span></div>
                <span class="kpi-badge" style="background:#f8fafc; color:#64748b;">כללי</span>
            </div>
            <div class="kpi-content">
                <div class="kpi-value-row">
                    <span class="kpi-unit">פעילים</span>
                    <span class="kpi-number">{val}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    #הגדרת עמודה ימנית - לא למחוק
    col_right, col_left = st.columns([1, 1])


    # ══════════════════════════════════════════════════════
    # עמודה ימנית
    # ══════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════
    # עמודה ימנית
    # ══════════════════════════════════════════════════════
    with col_right:
        
        # --- פרויקטים ---
        with st.container(border=True):
            st.markdown("### 📁 פרויקטים")
            with st.container(height=300, border=False):
                for _, row in projects.iterrows():
                    p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                    st.markdown(f'''
                        <a href="{p_url}" target="_self" class="project-link">
                            <div class="record-row">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <b>📂 {row["project_name"]}</b>
                                    <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                                </div>
                                <span style="color: #94a3b8; font-size: 22px; line-height: 1; flex-shrink: 0;">&#8250;</span>
                            </div>
                        </a>
                    ''', unsafe_allow_html=True)
    
        # --- משימות ---
        with st.container(border=True):
            st.markdown('<h3>📋 משימות חדשות azure </h3>', unsafe_allow_html=True)
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {})
                    t_id, t_title, p_task = t.get('id'), f.get('System.Title', ''), f.get('System.TeamProject', 'General')
                    raw_date = f.get('System.CreatedDate', '')
                    fmt_date = f"{raw_date[8:10]}/{raw_date[5:7]} {raw_date[11:16]}" if raw_date else ""
                    t_url = f"https://dev.azure.com/amandigital/{urllib.parse.quote(p_task)}/_workitems/edit/{t_id}"
    
                    st.markdown(
                        f'<div class="record-row" style="white-space: nowrap;">'
                        f'<div style="flex-grow: 1; text-align: right; overflow: hidden; text-overflow: ellipsis;">'
                        f'<a href="{t_url}" target="_blank" style="color: #0078d4; text-decoration: none; font-weight: 500;">🔗 {t_title}</a>'
                        f'<span style="color: #94a3b8; font-size: 0.8rem; margin-right: 15px;">נוצר ב {fmt_date}</span>'
                        f'</div>'
                        f'<span class="tag-orange" style="margin-right: 12px; flex-shrink: 0;">{p_task}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<p style="text-align: right; color: gray;">אין משימות חדשות.</p>', unsafe_allow_html=True)

        # ============================
        #      עוזר אישי AI — ורוד
        # ============================
        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")
    
            a1, a2 = st.columns([1, 2])
    
            sel_p = a1.selectbox(
                "פרויקט",
                ["כללי - כל הפרויקטים"] + projects["project_name"].tolist(),
                label_visibility="collapsed",
                key="ai_p"
            )
    
            q_in = a2.text_input(
                "שאלה",
                placeholder="מה תרצי לדעת?",
                label_visibility="collapsed",
                key="ai_i"
            )
    
            if st.button("שגר שאילתה 🚀", use_container_width=True):
                if q_in:
                    with st.spinner("מנתח..."):
                        try:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
                            projects_summary = "\n".join([
                                f"- {r['project_name']}: סטטוס {r.get('status','לא ידוע')}, סוג {r.get('project_type','לא ידוע')}"
                                for _, r in projects.iterrows()
                            ])
    
                            meetings_today = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
                            meetings_summary = "\n".join([
                                f"- {r['meeting_title']} בשעה {fmt_time(r.get('start_time',''))}"
                                for _, r in meetings_today.iterrows()
                            ]) if not meetings_today.empty else "אין פגישות היום"
    
                            reminders_today2 = st.session_state.rem_live[
                                pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today
                            ]
                            reminders_summary = "\n".join([
                                f"- {r['reminder_text']} ({r.get('project_name','כללי')})"
                                for _, r in reminders_today2.iterrows()
                            ]) if not reminders_today2.empty else "אין תזכורות"
    
                            tasks_summary = "\n".join([
                                f"- {t.get('fields',{}).get('System.Title','')} ({t.get('fields',{}).get('System.TeamProject','')})"
                                for t in (get_azure_tasks() or [])
                            ]) or "אין משימות פתוחות"
    
                            fathom_summaries = "\n".join([
                                f"- פגישה: {k.replace('sum_v4_','')}: {v[:200]}..."
                                for k, v in st.session_state.items()
                                if k.startswith("sum_v4_") and v
                            ]) or "אין סיכומי פגישות"
    
                            focus = (
                                f"התמקד בפרויקט: {sel_p}"
                                if sel_p != "כללי - כל הפרויקטים"
                                else "התייחס לכל הפרויקטים"
                            )
    
                            prompt = f"""אתה עוזר AI בכיר לניהול פרויקטים. יש לך גישה לכל המידע הבא:
    
    📁 פרויקטים:
    {projects_summary}
    
    📅 פגישות היום:
    {meetings_summary}
    
    🔔 תזכורות היום:
    {reminders_summary}
    
    📋 משימות פתוחות באז'ור:
    {tasks_summary}
    
    📝 סיכומי פגישות אחרונים:
    {fathom_summaries}
    
    {focus}
    שאלה: {q_in}
    
    ענה בעברית עסקית, בצורה מעמיקה וממוקדת. אם רלוונטי — תצלב מידע בין מקורות שונים."""
    
                            response = model.generate_content(prompt)
                            st.session_state.ai_response = response.text
    
                        except Exception as e:
                            st.session_state.ai_response = f"שגיאה: {str(e)}"
    
            if st.session_state.ai_response:
                st.info(st.session_state.ai_response)


        # ── פרויקטים לדיווח ─────────────────────────────────
        # ============================
        # 📌 פרויקטים לדיווח (priority.xlsx)
        # ============================
        with st.container(border=True):
            st.markdown("### 📌 פרויקטים לדיווח")
    
            if priority_df.empty:
                st.write("לא נמצאו פרויקטים לדיווח.")
            else:
                color_map = {
                    "אנליסט": "tag-blue",
                    "דנאל": "tag-green",
                    "דלק": "tag-orange",
                    "בנק": "tag-teal",
                    "פיתוח": "tag-pink",
                    "אלשטול": "tag-purple",
                }
    
                # --- חדש: session state לפתיחה/סגירה ---
                if "priority_expanded" not in st.session_state:
                    st.session_state.priority_expanded = False
    
                rows_to_show = priority_df if st.session_state.priority_expanded else priority_df.iloc[:4]
    
                for _, row in rows_to_show.iterrows():
                    project_name   = row["project_name"]
                    project_number = row["project_number"]
                    order_number   = row["order_number"]
                    category  = project_name.split(" ")[0]
                    tag_class = color_map.get(category, "tag-gray")
    
                    html = (
                        '<div class="record-row" '
                        'style="display:flex; align-items:center; justify-content:space-between; '
                        'gap:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
    
                            f'<span style="font-weight:600; overflow:hidden; text-overflow:ellipsis;">'
                            f'{project_name} '
                            f'<span style="color:#64748b; font-size:0.8rem; margin-right:6px;">'
                            f'{project_number} | {order_number}'
                            '</span>'
                            '</span>'
    
                            f'<span class="{tag_class}" style="white-space:nowrap; flex-shrink:0;">'
                            f'{category}</span>'
    
                        '</div>'
                    )
                    st.markdown(html, unsafe_allow_html=True)
    
                # --- כפתור הצג הכל / הראה פחות ---
                if len(priority_df) > 4:
                    label = "הראה פחות ▲" if st.session_state.priority_expanded else f"הצג הכל ({len(priority_df)}) ▼"
                    st.markdown("""
                        <style>
                        div[data-testid="stBaseButton-secondary"]:has(p) button,
                        .priority-link-btn button {
                            background: transparent !important;
                            border: none !important;
                            box-shadow: none !important;
                            color: #4facfe !important;
                            font-size: 0.82rem !important;
                            font-weight: 600 !important;
                            padding: 2px 0 !important;
                            margin-top: 4px !important;
                            text-align: right !important;
                            width: auto !important;
                            min-height: unset !important;
                            cursor: pointer !important;
                            float: right !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    if st.button(label, key="toggle_priority_btn"):
                        st.session_state.priority_expanded = not st.session_state.priority_expanded
                        st.rerun()

        
    # ══════════════════════════════════════════════════════
    # עמודה שמאלית
    # ══════════════════════════════════════════════════════
    with col_left:
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty:
                st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    s_t = fmt_time(r.get('start_time', ''))
                    e_t = fmt_time(r.get('end_time', ''))
                    st.markdown(f'<div class="record-row"><span style="flex-grow:1; text-align:right;">📌 {r["meeting_title"]}</span><span class="time-label">{s_t}-{e_t}</span></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")
            with st.container(border=False):
                t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
                if not t_r.empty:
                    for _, row in t_r.iterrows():
                        st.markdown(f'<div class="record-row"><span>🔔 {row["reminder_text"]}</span><span class="tag-orange">{row.get("project_name", "כללי")}</span></div>', unsafe_allow_html=True)
                else:
                    st.write("אין תזכורות להיום.")

            if st.session_state.adding_reminder:
                with st.container():
                    r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 3, 0.5, 0.5])
                    with r_col1: new_proj = st.selectbox("פרויקט", projects["project_name"].tolist() + ["כללי"], label_visibility="collapsed", key="new_rem_proj")
                    with r_col2: new_text = st.text_input("תיאור", placeholder="מה להזכיר?", label_visibility="collapsed", key="new_rem_text")
                    with r_col3:
                        if st.button("✅", key="save_rem_btn"):
                            if new_text:
                                new_row = {"date": today, "reminder_text": new_text, "project_name": new_proj}
                                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([new_row])], ignore_index=True)
                                st.session_state.adding_reminder = False; st.rerun()
                    with r_col4:
                        if st.button("❌", key="cancel_rem_btn"):
                            st.session_state.adding_reminder = False; st.rerun()
            else:
                if st.button("➕ הוספת תזכורת", use_container_width=True):
                    st.session_state.adding_reminder = True; st.rerun()

        # ── Fathom ──────────────────────────────────────────
        # ── Fathom ──────────────────────────────────────────
        with st.container(border=True):
            col_title, col_refresh = st.columns([0.9, 0.1])
            with col_title:
                st.markdown("### ✨ סיכומי פגישות Fathom")
            with col_refresh:
                if st.button("🔄", key="refresh_fathom"):
                    try:
                        items, status = get_fathom_meetings()
                        if status == 200:
                            st.session_state['fathom_meetings'] = items
                            st.rerun()
                    except: pass

            if 'fathom_meetings' not in st.session_state:
                try:
                    items, status = get_fathom_meetings()
                    st.session_state['fathom_meetings'] = items if status == 200 else []
                except:
                    st.session_state['fathom_meetings'] = []

            st.markdown("""
                <style>
                .fathom-row-ui {
                    display: grid;
                    grid-template-columns: auto 1fr auto;
                    align-items: center;
                    background: white;
                    border: 1px solid #edf2f7;
                    border-right: 5px solid #4facfe;
                    border-radius: 8px;
                    padding: 0 16px;
                    height: 45px;
                    direction: rtl;
                    transition: all 0.2s ease;
                }
                div[data-testid="stVerticalBlock"] > div:has(.fathom-row-ui) { gap: 0rem !important; }
                div.element-container:has(.fathom-row-ui) + div.element-container {
                    margin-top: -45px !important; margin-bottom: 2px !important;
                }
                div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button {
                    background: transparent !important; border: 1px solid transparent !important;
                    border-right: 5px solid transparent !important; width: 100% !important;
                    height: 45px !important; color: transparent !important; z-index: 20;
                }
                div.element-container:has(.fathom-row-ui):has(+ div.element-container div[data-testid="stButton"] button:hover) .fathom-row-ui {
                    border-color: #4facfe; background-color: #f8fafc; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }
                .fathom-pill-v2 {
                    background-color: #f1f5f9; color: #475569;
                    padding: 1px 8px; border-radius: 10px; font-size: 0.75rem; margin-right: 12px;
                }
                div[data-testid="stAlert"] p  { direction: rtl !important; text-align: right !important; }
                div[data-testid="stAlert"] ul { padding-right: 20px !important; padding-left: 0 !important; text-align: right !important; }
                div[data-testid="stAlert"] ol { padding-right: 20px !important; padding-left: 0 !important; text-align: right !important; }
                div[data-testid="stAlert"] li { text-align: right !important; }
                div[data-testid="stAlert"] h1,
                div[data-testid="stAlert"] h2,
                div[data-testid="stAlert"] h3 { font-size: 1.1rem !important; font-weight: 700 !important; color: #1d6fa4 !important; }
                </style>
            """, unsafe_allow_html=True)

            f_meetings = st.session_state.get('fathom_meetings', [])
            if f_meetings:
                for idx, mtg in enumerate(f_meetings):
                    rec_id   = mtg.get('recording_id')
                    title    = mtg.get('title') or "פגישה"
                    date_str = mtg.get('recording_start_time', '')[:10]
                    open_key = f"open_{rec_id}"
                    is_open  = st.session_state.get(open_key, False)
                    s_key    = f"sum_v4_{rec_id}"

                    # תיקון החץ — Unicode במקום Material Symbols
                    arrow = "&#8250;" if not is_open else "&#8249;"

                    st.markdown(f'''
                        <div class="fathom-row-ui">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.1rem; margin-left: 10px;">📅</span>
                                <span style="font-weight: 600; color: #1e293b; font-size: 0.85rem;">{title}</span>
                                <span class="fathom-pill-v2">{date_str}</span>
                            </div>
                            <div></div>
                            <span style="color: #94a3b8; font-size: 22px; line-height: 1; flex-shrink: 0;">{arrow}</span>
                        </div>
                    ''', unsafe_allow_html=True)

                    if st.button("", key=f"f_trig_{rec_id}_{idx}", use_container_width=True):
                        st.session_state[open_key] = not is_open
                        st.rerun()

                    if is_open:
                        with st.container():
                            if s_key not in st.session_state:
                                if st.button("צור סיכום עם AI 🪄", key=f"gen_{rec_id}"):
                                    with st.spinner("מנתח..."):
                                        raw = get_fathom_summary(rec_id)
                                        if raw:
                                            summary = refine_with_ai(raw)
                                            st.session_state[s_key] = summary
                                            save_summary_to_excel(title, date_str, summary)
                                        else:
                                            st.session_state[s_key] = "לא נמצא תוכן לסיכום"
                            if st.session_state.get(s_key):
                                st.info(st.session_state.get(s_key))
                                
