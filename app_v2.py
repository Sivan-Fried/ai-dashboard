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

# 2. הזרקת עיצוב גלובלית מאוחדת
st.markdown("""
<style>
    /* 1. הסרת המרווח הלבן של הדף כולו */
    .stApp .main .block-container {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    /* 2. המשיכה האגרסיבית של תיבת הציטוט למעלה */
    .premium-quote-box-refined {
        width: 100%;
        background: #ffffff;
        background-image: radial-gradient(circle at 10% 50%, rgba(250, 220, 230, 0.4) 0%, transparent 45%), 
                          radial-gradient(circle at 90% 80%, rgba(227, 225, 236, 0.3) 0%, transparent 45%);
        border-bottom: 1px solid #f1f5f9;
        text-align: center;
        direction: rtl;
        
        /* התיקון הקריטי: הזזה אבסולוטית כלפי מעלה */
        position: relative !important;
        top: -13px !important; /* ככל שתגדילי את המספר השלילי, זה יעלה יותר גבוה */
        
        /* צמצום הפאדינג הפנימי כדי שהתיבה עצמה תהיה דקה יותר */
        padding: 25px 60px 10px 60px !important;
        
        /* צמצום הרווח מה-KPIs (ערך שלילי כאן מקרב את ה-KPIs לציטוט) */
        margin-bottom: -70px !important; 
        
        z-index: 1 !important;
    }

    /* 3. שמירה על הסרגל הלבן (Header) מעל הציטוט */
    header[data-testid="stHeader"] {
        background-color: white !important;
        z-index: 1000 !important;
    }
</style>
""", unsafe_allow_html=True)

# טעינת פונטים — Material Symbols Rounded לאייקונים, Plus Jakarta Sans לטקסט
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" />', unsafe_allow_html=True)

# טעינת קובץ העיצוב החיצוני — styles_v2.css
with open("styles_v2.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
section[data-testid="stMain"] > div {
    padding-top: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

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
    margin-top: -45px;
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
    margin: 0 !important;
    padding: 0 !important;
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

def render_sidebar(page="main"):
    import streamlit.components.v1 as components
    
    if page == "main":
        nav_items = [
            {"icon": "dashboard", "label": "דשבורד", "target": "section-projects"},
            {"icon": "calendar_today", "label": "פגישות", "target": "section-meetings"},
            {"icon": "checklist", "label": "משימות", "target": "section-tasks"},
            {"icon": "notifications", "label": "תזכורות", "target": "section-reminders"},
            {"icon": "edit", "label": "דיווחים", "target": "section-priority"},
            {"icon": "description", "label": "סיכומים", "target": "section-fathom"},
            {"icon": "smart_toy", "label": "עוזר AI", "target": "section-ai"},
        ]
    else:
        nav_items = [
            {"icon": "calendar_month", "label": "תוכנית עבודה", "target": "tab-work"},
            {"icon": "group", "label": "משאבים", "target": "tab-resources"},
            {"icon": "warning", "label": "סיכונים", "target": "tab-risks"},
            {"icon": "description", "label": "סיכומים", "target": "tab-meetings"},
        ]

    components.html(f"""<!DOCTYPE html>
<html dir="rtl">
<head><meta charset="utf-8"/></head>
<body>
<script>
var parentDoc = window.parent.document;

var oldSidebar = parentDoc.getElementById('aura-sidebar');
if (oldSidebar) oldSidebar.remove();
var oldStyle = parentDoc.getElementById('aura-sidebar-style');
if (oldStyle) oldStyle.remove();

var style = parentDoc.createElement('style');
style.id = 'aura-sidebar-style';
style.textContent = `
    #aura-sidebar {{
        position: fixed;
        right: 16px;
        top: 120px;
        width: 180px;
        background: white;
        border-radius: 16px;
        border: 1px solid #F4F4F5;
        box-shadow: 0 2px 20px rgba(225,200,210,0.2);
        padding: 12px 8px;
        z-index: 99999;
        transition: width 0.3s ease;
        font-family: 'Plus Jakarta Sans', sans-serif;
        direction: rtl;
    }}
    #aura-sidebar.collapsed {{ width: 52px; }}
    .aura-toggle-btn {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #fdf2f8;
        cursor: pointer;
        margin: 0 auto 8px auto;
        border: none;
        color: #f0b8cb;
        font-size: 18px;
        transition: all 0.2s;
    }}
    .aura-toggle-btn:hover {{ background: #fadce6; }}
    .aura-nav-item {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 12px;
        cursor: pointer;
        color: #71717A;
        transition: all 0.2s ease;
        white-space: nowrap;
        overflow: hidden;
    }}
    .aura-nav-item:hover {{ background: #fdf2f8; color: #3f3f46; }}
    .aura-nav-icon {{
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        flex-shrink: 0;
        color: #94a3b8;
        line-height: 1;
    }}
    .aura-nav-item:hover .aura-nav-icon {{ color: #f0b8cb; }}
    .aura-nav-label {{
        font-size: 0.82rem;
        font-weight: 500;
        white-space: nowrap;
        transition: opacity 0.2s, width 0.2s;
    }}
    #aura-sidebar.collapsed .aura-nav-label {{
        opacity: 0;
        width: 0;
        overflow: hidden;
    }}
`;
parentDoc.head.appendChild(style);

var navItems = {str(nav_items).replace("'", '"')};

var itemsHtml = '';
navItems.forEach(function(item) {{
    itemsHtml += '<div class="aura-nav-item" onclick="auraScrollTo(\\''+item.target+'\\')"><span class="aura-nav-icon">'+item.icon+'</span><span class="aura-nav-label">'+item.label+'</span></div>';
}});

var sidebar = parentDoc.createElement('div');
sidebar.id = 'aura-sidebar';
sidebar.innerHTML = '<button class="aura-toggle-btn" id="aura-toggle" onclick="auraToggle()">&#10094;</button>' + itemsHtml;
parentDoc.body.appendChild(sidebar);


window.auraToggle = function() {{
    var sb = parentDoc.getElementById('aura-sidebar');
    var btn = parentDoc.getElementById('aura-toggle');
    sb.classList.toggle('collapsed');
    btn.innerHTML = sb.classList.contains('collapsed') ? '&#10095;' : '&#10094;';
}};

window.auraScrollTo = function(id) {{
    var el = parentDoc.getElementById(id);
    if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}};
</script>
</body>
</html>""", height=0, scrolling=False)


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
today_reminders = st.session_state.rem_live[
    pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today
].copy()

if 'status' in today_reminders.columns:
    today_reminders['is_read'] = today_reminders['status'].apply(lambda x: x in [True, 1, 'read'])
elif 'is_read' not in today_reminders.columns:
    today_reminders['is_read'] = False

render_topbar_with_bell(img_b64, w_text, w_city, greeting, today_reminders)
render_sidebar(page=st.session_state.current_page)

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
    
    
    # ── Daily Quote Section Logic & Display ──────────────────────────
    import streamlit as st
    import pandas as pd
    import os
    
    # 1. לוגיקה של שליפת הנתונים
    quote_text = "מה שלא תעשה או שתחלום שאתה יכול לעשות - התחל עם זה"
    quote_author = "יוהאן וולפגנג פון גתה"
    try:
        if os.path.exists("inspirational_quotes.xlsx"):
            df = pd.read_excel("inspirational_quotes.xlsx", engine='openpyxl')
            if not df.empty:
                row = df.sample(n=1).iloc[0]
                q_col = [c for c in df.columns if str(c).lower() in ['quote', 'ציטוט']]
                a_col = [c for c in df.columns if str(c).lower() in ['author', 'מחבר']]
                if q_col: quote_text = str(row[q_col[0]])
                if a_col: quote_author = str(row[a_col[0]])
    except: pass
    
    # 2. ה-CSS המלוטש והנקי
    st.markdown(f"""
    <style>
        header[data-testid="stHeader"] {{
            background-color: white !important;
            z-index: 1000 !important;
        }}
    
        .stApp .main .block-container {{
            padding-top: 0px !important;
            margin-top: -5.5rem !important; 
        }}
    
        .premium-quote-box-refined {{
            background: #ffffff;
            background-image: radial-gradient(circle at 10% 50%, rgba(250, 220, 230, 0.4) 0%, transparent 45%), 
                              radial-gradient(circle at 90% 80%, rgba(227, 225, 236, 0.3) 0%, transparent 45%);
            border-bottom: 1px solid #f1f5f9;
            padding: 25px 60px 10px 60px !important;
            text-align: center;
            direction: rtl;
            position: relative;
            width: 100%;
            box-sizing: border-box;
            margin-bottom: 0px !important; 
            z-index: 1;
        }}
    
        .premium-quote-box-refined::before {{
            content: '“'; position: absolute; top: 10px; right: 40px;
            font-size: 100px; color: #fadce6; font-family: serif; opacity: 0.5; line-height: 1;
        }}
    
        .premium-quote-box-refined::after {{
            content: '”'; position: absolute; bottom: -15px; left: 40px;
            font-size: 100px; color: #fadce6; font-family: serif; opacity: 0.5; line-height: 1;
        }}
    
        .q-main-text {{
            font-family: 'Noto Serif Hebrew', serif !important;
            font-size: 20px !important; 
            color: #1a1c1c !important;
            font-weight: 700 !important;
            line-height: 1.3;
            margin: 5px 12% !important;
            position: relative;
            z-index: 2;
        }}
    
        .q-author-text {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 13px;
            color: #646566;
            font-style: italic;
            display: block;
            margin-bottom: 5px;
        }}
    
        .material-symbols-outlined {{
            font-family: 'Material Symbols Outlined' !important;
            color: #e59fb5 !important; /* ורוד עדין ומדויק לאייקון */
            font-size: 22px !important;
            vertical-align: middle;
        }}
    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&family=Noto+Serif+Hebrew:wght@700&family=Material+Symbols+Outlined" rel="stylesheet">
    
    <div class="premium-quote-box-refined">
        <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 9px; font-weight: 600; color: #6f5861; text-transform: uppercase; letter-spacing: 0.2em; display: block; margin-bottom: 5px; opacity: 0.6;">DAILY QUOTE</span>
        <div class="q-main-text">"{quote_text}"</div>
        <span class="q-author-text">&#8212; {quote_author} &#8212;</span>
        <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 5px;">
            <div style="height: 1px; width: 40px; background-color: #fadce6;"></div>
            <span class="material-symbols-outlined">auto_stories</span>
            <div style="height: 1px; width: 40px; background-color: #fadce6;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
                                                                                


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
    
    #st.markdown("<br>", unsafe_allow_html=True
    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    #הגדרת עמודה ימנית - לא למחוק
    col_right, col_left = st.columns([1, 1])


    # ══════════════════════════════════════════════════════
    # עמודה ימנית
    # ══════════════════════════════════════════════════════
    with col_right:
        
        # --- פרויקטים ---
        st.markdown('<div id="section-projects"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### <span class=\"material-symbols-outlined\" style=\"vertical-align: middle; margin-left: 8px; font-size: 1.5rem; color: #64748b;\">work</span> פרויקטים", unsafe_allow_html=True)
            
            # הסרנו את ה-height הקשיח כדי לצמצם את הרווח הגדול, והשארנו את התצוגה פתוחה או מותאמת
            with st.container(border=False):
                for _, row in projects.iterrows():
                    p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                    st.markdown(f'''
                        <a href="{p_url}" target="_self" class="project-link">
                            <div class="record-row">
                                <span style="display: flex; align-items: center; gap: 10px; font-size: 0.92rem; font-weight: normal;">
                                    <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 18px; width: 20px; height: 20px; color: #64748b; transform: scale(0.8);">work</span>
                                    {row["project_name"]}
                                </span>
                                <span style="display: flex; align-items: center; gap: 10px;">
                                    <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                                    <span style="color: #94a3b8; font-size: 22px; line-height: 1; flex-shrink: 0; margin-right: 2px;">&#8250;</span>
                                </span>
                            </div>
                        </a>
                    ''', unsafe_allow_html=True)


        #אזור תזכורות
        # --- אזור תזכורות ---
        with st.container(border=True):
            st.markdown('<div id="section-reminders"></div>', unsafe_allow_html=True)
            st.markdown("### <span class=\"material-symbols-outlined\" style=\"vertical-align: middle; margin-left: 8px; font-size: 1.5rem; color: #64748b;\">notifications</span> תזכורות", unsafe_allow_html=True)
            with st.container(border=False):
                t_r = st.session_state.rem_live[pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today]
                if not t_r.empty:
                    for _, row in t_r.iterrows():
                        st.markdown(f'''
                            <div class="record-row">
                                <span style="display: flex; align-items: center; gap: 8px; font-size: 0.92rem; font-weight: normal;">
                                    <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 18px; width: 20px; height: 20px; color: #64748b; transform: scale(0.8);">notifications</span>
                                    {row["reminder_text"]}
                                </span>
                                <span class="tag-orange">{row.get("project_name", "כללי")}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.write("אין תזכורות להיום.")
        
            if st.session_state.adding_reminder:
                with st.container():
                    r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 3, 0.5, 0.5])
                    with r_col1: new_proj = st.selectbox("פרויקט", projects["project_name"].tolist() + ["כללי"], label_visibility="collapsed", key="new_rem_proj")
                    with r_col2: new_text = st.text_input("תיאור", placeholder="מה להזכיר?", label_visibility="collapsed", key="new_rem_text")
                    with r_col3:
                        if st.button("✓", key="save_rem_btn"):
                            if new_text:
                                new_row = {"date": today, "reminder_text": new_text, "project_name": new_proj}
                                st.session_state.rem_live = pd.concat([st.session_state.rem_live, pd.DataFrame([new_row])], ignore_index=True)
                                st.session_state.adding_reminder = False; st.rerun()
                    with r_col4:
                        if st.button("×", key="cancel_rem_btn"):
                            st.session_state.adding_reminder = False; st.rerun()
            else:
                if st.button("+", use_container_width=True, key="add_rem_btn_unique", type="secondary"):
                    st.session_state.adding_reminder = True
                    st.rerun()
                    
        # --- משימות ---
        # --- משימות ---
        with st.container(border=True):
            st.markdown('<div id="section-tasks"></div>', unsafe_allow_html=True)
            st.markdown('<h3><span class="material-symbols-outlined" style="vertical-align: middle; margin-left: 8px; font-size: 1.5rem; color: #64748b;">checklist</span> משימות חדשות azure </h3>', unsafe_allow_html=True)
            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {})
                    t_id, t_title, p_task = t.get('id'), f.get('System.Title', ''), f.get('System.TeamProject', 'General')
                    raw_date = f.get('System.CreatedDate', '')
                    fmt_date = f"{raw_date[8:10]}/{raw_date[5:7]} {raw_date[11:16]}" if raw_date else ""
                    t_url = f"https://dev.azure.com/amandigital/{urllib.parse.quote(p_task)}/_workitems/edit/{t_id}"
                    st.markdown(
                        f'''
                        <div class="record-row" style="white-space: nowrap;">
                            <span style="display: flex; align-items: center; gap: 8px; flex-grow: 1; text-align: right; overflow: hidden; text-overflow: ellipsis; font-size: 0.92rem; font-weight: normal;">
                                <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 18px; width: 20px; height: 20px; color: #0078d4; transform: scale(0.8);">checklist</span>
                                <a href="{t_url}" target="_blank" style="color: #0078d4; text-decoration: underline; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{t_title}</a>
                                <span style="color: #94a3b8; font-size: 0.75rem; margin-right: 15px; flex-shrink: 0;">נוצר ב {fmt_date}</span>
                            </span>
                            <span class="tag-orange" style="margin-right: 12px; flex-shrink: 0;">{p_task}</span>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<p style="text-align: right; color: gray;">אין משימות חדשות.</p>', unsafe_allow_html=True)
                
                        

        # ============================
        # 📌 פרויקטים לדיווח (priority.xlsx)
        # ============================
        with st.container(border=True):
            st.markdown('<div id="section-priority"></div>', unsafe_allow_html=True)
            st.markdown('<h3><span class="material-symbols-outlined" style="vertical-align: middle; margin-left: 8px; font-size: 1.5rem; color: #64748b;">edit</span> פרויקטים לדיווח</h3>', unsafe_allow_html=True)
            
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
                        'gap:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; '
                        'font-size:0.92rem; font-weight:normal;">'
                            '<span style="display: flex; align-items: center; gap: 8px; overflow:hidden; text-overflow:ellipsis;">'
                                f'<span class="material-symbols-outlined" style="vertical-align: middle; font-size: 18px; width: 20px; height: 20px; color: #64748b; transform: scale(0.8);">edit</span>'
                                f'<span style="overflow:hidden; text-overflow:ellipsis; font-weight:normal;">'
                                    f'{project_name} '
                                    f'<span style="color:#64748b; font-size:0.75rem; margin-right:6px;">'
                                        f'{project_number} | {order_number}'
                                    f'</span>'
                                f'</span>'
                            f'</span>'
                            f'<span class="{tag_class}" style="white-space:nowrap; flex-shrink:0;">'
                            f'{category}</span>'
                        '</div>'
                    )
                    st.markdown(html, unsafe_allow_html=True)
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
        #אזור פגישות
        with st.container(border=True):
            st.markdown('<div id="section-meetings"></div>', unsafe_allow_html=True)
            st.markdown("### <span class=\"material-symbols-outlined\" style=\"vertical-align: middle; margin-left: 8px; color: #6f5861;\">calendar_today</span> פגישות היום", unsafe_allow_html=True)
            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]
            if t_m.empty:
                st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    s_t = fmt_time(r.get('start_time', ''))
                    e_t = fmt_time(r.get('end_time', ''))
                    st.markdown(f'''
                        <div class="record-row">
                            <span style="display: flex; align-items: center; gap: 8px; flex-grow: 1; text-align: right; font-size: 0.92rem; font-weight: normal;">
                                <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 18px; width: 20px; height: 20px; color: #6f5861; transform: scale(0.8);">event_available</span>
                                {r["meeting_title"]}
                            </span>
                            <span class="time-label">{s_t}-{e_t}</span>
                        </div>
                    ''', unsafe_allow_html=True)

                
                                        
        # ── Fathom ──────────────────────────────────────────
        # ── Fathom ──────────────────────────────────────────
        # ── Fathom ──────────────────────────────────────────
        with st.container(border=True):
            st.markdown('<div id="section-fathom"></div>', unsafe_allow_html=True)
            col_title, col_refresh = st.columns([0.9, 0.1])
            with col_title:
                st.markdown('<h3><span class="material-symbols-outlined" style="vertical-align: middle; margin-left: 8px; font-size: 1.5rem; color: #64748b;">description</span> סיכומי פגישות Fathom</h3>', unsafe_allow_html=True)
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
                div[data-testid="stVerticalBlock"] > div:has(.fathom-row-ui) { gap: 0rem !important; }
                div.element-container:has(.fathom-row-ui) + div.element-container {
                    margin-top: -45px !important; margin-bottom: 0px !important;
                }
                div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button {
                    background: transparent !important; border: 1px solid transparent !important;
                    border-right: 5px solid transparent !important; width: 100% !important;
                    height: 45px !important; color: transparent !important; z-index: 20;
                }
                div.element-container:has(.fathom-row-ui):has(+ div.element-container div[data-testid="stButton"] button:hover) .fathom-row-ui {
                    border-right-color: #f0b8cb !important;
                    background-color: #fdf6f9 !important;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
                }
                </style>
            """, unsafe_allow_html=True)

            f_meetings = st.session_state.get('fathom_meetings', [])
            if f_meetings:
                for idx, mtg in enumerate(f_meetings):
                    rec_id   = mtg.get('recording_id')
                    title    = mtg.get('title') or "פגישה"
                    raw_date = mtg.get('recording_start_time', '')[:10]
                    if raw_date and len(raw_date) >= 10:
                        date_str = f"{raw_date[8:10]}-{raw_date[5:7]}-{raw_date[0:4]}"
                    else:
                        date_str = ""
                    open_key = f"open_{rec_id}"
                    is_open  = st.session_state.get(open_key, False)
                    s_key    = f"sum_v4_{rec_id}"
                    arrow = "&#8250;" if not is_open else "&#8249;"
                    st.markdown(f'''
                        <div class="fathom-row-ui" style="font-size: 0.92rem; font-weight: normal;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 18px; width: 20px; height: 20px; color: #64748b; transform: scale(0.8);">description</span>
                                <span style="font-size: 0.88rem;">{title}</span>
                            </div>
                            <div style="display: flex; justify-content: flex-end; align-items: center;">
                                <span class="fathom-pill-v2">{date_str}</span>
                            </div>
                            <span style="color: #94a3b8; font-size: 22px; line-height: 1; flex-shrink: 0; margin-right: 8px;">{arrow}</span>
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

        # ============================
        #      עוזר אישי AI — ורוד
        # ============================
        with st.container(border=True, key="ai_container"):
            st.markdown('<div id="section-ai"></div>', unsafe_allow_html=True)
            st.markdown('### <span class="material-symbols-outlined" style="vertical-align: middle; margin-left: 8px; font-size: 1.5rem; color: #64748b !important;">smart_toy</span> עוזר AI אישי', unsafe_allow_html=True)

            sel_p = st.selectbox(
                "פרויקט",
                ["בחר פרויקט לניתוח..."] + projects["project_name"].tolist(),
                label_visibility="collapsed",
                key="ai_p"
            )

            q_in = st.text_area(
                "שאלה",
                placeholder="מה תרצי לדעת?",
                label_visibility="collapsed",
                key="ai_i",
                height=100
            )

            col_empty, col_btn = st.columns([0.89, 0.11])
            with col_btn:
                send = st.button("↩", key="ai_send", use_container_width=True)

            if send:
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
