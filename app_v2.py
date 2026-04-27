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

# טעינת פונטים — Material Symbols Rounded לאייקונים, Plus Jakarta Sans לטקסט
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" />', unsafe_allow_html=True)

# טעינת קובץ העיצוב החיצוני — styles_v2.css
with open("styles_v2.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#ai-card
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
#ניסיון להוסיף סרגל עליון
# =========================================================
# סרגל עליון — פרופיל + ניווט + מזג אוויר + שעה + פעמון
# =========================================================
def render_topbar(img_b64, w_text, w_city, greeting):
    import re
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%d/%m/%Y")
    # ניקוי אמוג'י ממזג האוויר + הוספת סימן מעלות
    w_text_clean = re.sub(r'[^\x00-\x7F]+', '', w_text).strip()
    w_text_clean = w_text_clean.replace('C', '\u00b0C')
    # תמונת פרופיל
    profile_tag = f'<img src="data:image/png;base64,{img_b64}" style="width:82px;height:82px;border-radius:50%;object-fit:cover;object-position:center 20%;border:4px solid white;box-shadow:0 2px 12px rgba(225,200,210,0.4);"/>' if img_b64 else ""

    # מבנה הסרגל
    html = '<div style="background:white;border-radius:16px;border:1px solid #F4F4F5;box-shadow:0 2px 20px rgba(225,200,210,0.2);display:flex;align-items:center;justify-content:space-between;padding:20px 24px;direction:rtl;font-family:sans-serif;margin-bottom:20px;margin-top:-60px;">'

    # ימין: פרופיל + ברכה
    html += '<div style="display:flex;align-items:center;gap:10px;">'
    html += profile_tag
    html += '<div>'
    html += f'<div style="font-size:1rem;font-weight:700;color:#3f3f46;">{greeting}, סיון</div>'
    html += '<div style="font-size:0.8rem;color:#a1a1aa;">מנהלת פרויקטים</div>'
    html += '</div></div>'

    # מרכז: ניווט
    html += '<nav style="display:flex;gap:4px;flex:1;justify-content:center;">'
    html += '<span style="font-size:0.82rem;font-weight:600;padding:6px 14px;border-radius:20px;background:#FADCE6;color:#3f3f46;">דשבורד</span>'
    html += '<span style="font-size:0.82rem;padding:6px 14px;border-radius:20px;color:#71717A;">פרויקטים</span>'
    html += '<span style="font-size:0.82rem;padding:6px 14px;border-radius:20px;color:#71717A;">פגישות</span>'
    html += '<span style="font-size:0.82rem;padding:6px 14px;border-radius:20px;color:#71717A;">משימות</span>'
    html += '<span style="font-size:0.82rem;padding:6px 14px;border-radius:20px;color:#71717A;">דוחות</span>'
    html += '</nav>'

    # שמאל: מזג אוויר + שעה + שם + פעמון
    html += '<div style="display:flex;align-items:center;gap:12px;">'

    # אייקון טמפרטורה + מזג אוויר
    html += '<div style="display:flex;align-items:center;gap:6px;">'
    html += '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 11V5C12 3.34315 13.3431 2 15 2C16.6569 2 18 3.34315 18 5V11M12 11C10.3431 11 9 12.3431 9 14C9 15.6569 10.3431 17 12 17C13.6569 17 15 15.6569 15 14C15 12.3431 13.6569 11 12 11Z" stroke="#a1a1aa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    html += f'<div style="text-align:right;"><div style="font-size:0.82rem;font-weight:600;color:#3f3f46;">{w_text_clean}</div><div style="font-size:0.68rem;color:#a1a1aa;">{w_city}</div></div>'
    html += '</div>'

    html += '<div style="width:1px;height:28px;background:#F4F4F5;"></div>'

    # שעה ותאריך
    html += f'<div style="text-align:right;"><div style="font-size:0.85rem;font-weight:700;color:#3f3f46;">{time_str}</div><div style="font-size:0.68rem;color:#a1a1aa;">{date_str}</div></div>'

    html += '<div style="width:1px;height:28px;background:#F4F4F5;"></div>'

    # שם הדשבורד
    html += '<div style="font-size:1rem;font-weight:800;color:#f0b8cb;">Dashboard AI</div>'

    html += '<div style="width:1px;height:28px;background:#F4F4F5;"></div>'

    # אייקון פעמון SVG
    html += '<div id="topbar-bell" style="position:relative;display:inline-block;cursor:pointer;" onclick="document.getElementById(\'bellBtn\').click()">'
    html += '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 8C18 6.4087 17.3679 4.88258 16.2426 3.75736C15.1174 2.63214 13.5913 2 12 2C10.4087 2 8.88258 2.63214 7.75736 3.75736C6.63214 4.88258 6 6.4087 6 8C6 15 3 17 3 17H21C21 17 18 15 18 8Z" stroke="#71717A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M13.73 21C13.5542 21.3031 13.3019 21.5547 12.9982 21.7295C12.6946 21.9044 12.3504 21.9965 12 21.9965C11.6496 21.9965 11.3054 21.9044 11.0018 21.7295C10.6981 21.5547 10.4458 21.3031 10.27 21" stroke="#71717A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    html += '</div>'

    html += '</div>'
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


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

def render_notification_bell(reminders_today):
    unread = len(reminders_today)

    items_html = ""
    if reminders_today.empty:
        items_html = '<div class="sn-empty">אין תזכורות להיום 🎉</div>'
    else:
        for _, row in reminders_today.iterrows():
            text = str(row.get("reminder_text", "")).replace('"', '&quot;').replace("'", "&#39;").replace("<", "&lt;")
            proj = str(row.get("project_name", "כללי")).replace('"', '&quot;').replace("'", "&#39;")
            items_html += f"""
            <div class="sn-item">
                <div class="sn-dot"></div>
                <div>
                    <div class="sn-text">{text}</div>
                    <div class="sn-proj">{proj}</div>
                </div>
            </div>"""

    items_js = items_html.replace('`', r'\`').replace('\\', '\\\\')

    components.html(f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; font-family:'Segoe UI',Arial,sans-serif; }}
  body {{
    background:transparent; display:flex; justify-content:flex-start;
    align-items:center; height:60px; overflow:hidden; padding:4px;
  }}
  .bell-wrap {{ position:relative; display:inline-block; }}
  .bell-btn {{
    background:white; border:1px solid #e2e8f0; border-radius:50%;
    width:42px; height:42px; font-size:1.2rem; cursor:pointer;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
    display:flex; align-items:center; justify-content:center;
    transition:all 0.2s; outline:none;
  }}
  .bell-btn:hover {{ background:#f0f9ff; }}
  .badge {{
    position:absolute; top:-5px; left:-5px;
    background:#ef4444; color:white; border-radius:50%;
    min-width:18px; height:18px; font-size:0.65rem; font-weight:800;
    display:{'flex' if unread > 0 else 'none'};
    align-items:center; justify-content:center;
    border:2px solid white; z-index:10; padding:0 3px;
  }}
</style>
</head>
<body>
  <div class="bell-wrap">
    <span class="badge" id="badge">{unread}</span>
    <button class="bell-btn" id="bellBtn">🔔</button>
  </div>
<script>
  var isOpen = false;

  window.addEventListener('load', function() {{
    var parentDoc = window.parent.document;

    var old = parentDoc.getElementById('sn-floating-dropdown');
    if (old) old.remove();
    var oldStyle = parentDoc.getElementById('sn-styles');
    if (oldStyle) oldStyle.remove();

    var style = parentDoc.createElement('style');
    style.id = 'sn-styles';
    style.textContent = `
      #sn-floating-dropdown {{
        display:none; position:fixed; width:320px; background:white;
        border-radius:14px; box-shadow:0 8px 30px rgba(0,0,0,0.18);
        border:1px solid #edf2f7; z-index:999999; overflow:hidden;
        direction:rtl; font-family:'Segoe UI',Arial,sans-serif;
      }}
      @keyframes snFadeIn {{
        from {{ opacity:0; transform:translateY(-8px); }}
        to   {{ opacity:1; transform:translateY(0); }}
      }}
      .sn-header {{
        padding:13px 16px; font-weight:700; font-size:0.95rem;
        color:#1f2a44; border-bottom:1px solid #f1f5f9; background:#f8fafc;
      }}
      .sn-item {{
        padding:12px 16px; display:flex; align-items:center; gap:10px;
        cursor:pointer; border-bottom:1px solid #f8fafc; transition:background 0.15s;
      }}
      .sn-item:last-child {{ border-bottom:none; }}
      .sn-item:hover {{ background:#f0f9ff; }}
      .sn-item.read {{ opacity:0.4; }}
      .sn-item.read .sn-dot {{ background:#cbd5e1 !important; }}
      .sn-dot {{ width:9px; height:9px; border-radius:50%; background:#4facfe; flex-shrink:0; }}
      .sn-text {{ font-size:0.83rem; color:#1e293b; font-weight:500; }}
      .sn-proj {{ font-size:0.73rem; color:#94a3b8; margin-top:2px; }}
      .sn-empty {{ padding:24px 16px; text-align:center; color:#94a3b8; font-size:0.85rem; }}
    `;
    parentDoc.head.appendChild(style);

    var dropdown = parentDoc.createElement('div');
    dropdown.id = 'sn-floating-dropdown';
    dropdown.innerHTML = `
      <div class="sn-header">🔔 התזכורות שלך להיום</div>
      {items_js}
    `;
    parentDoc.body.appendChild(dropdown);

    dropdown.querySelectorAll('.sn-item').forEach(function(item) {{
      item.addEventListener('click', function() {{
        item.classList.add('read');
        var unreadCount = dropdown.querySelectorAll('.sn-item:not(.read)').length;
        var badge = document.getElementById('badge');
        if (unreadCount === 0) badge.style.display = 'none';
        else {{ badge.style.display = 'flex'; badge.textContent = unreadCount; }}
      }});
    }});

    parentDoc.addEventListener('click', function(e) {{
      var d = parentDoc.getElementById('sn-floating-dropdown');
      if (d && d.style.display === 'block' && !d.contains(e.target)) {{
        d.style.display = 'none';
        isOpen = false;
      }}
    }}, true);

    // עדכון מיקום בגלילה — כך החלונית נשארת מתחת לפעמון
    parentDoc.addEventListener('scroll', function() {{
      var d = parentDoc.getElementById('sn-floating-dropdown');
      if (d && d.style.display === 'block') {{
        var iframe = window.frameElement;
        var rect   = iframe.getBoundingClientRect();
        d.style.top   = (rect.bottom + 8) + 'px';
        d.style.right = (parentDoc.documentElement.clientWidth - rect.right) + 'px';
      }}
    }}, true);
  }});

  document.getElementById('bellBtn').addEventListener('click', function() {{
    var parentDoc = window.parent.document;
    var d = parentDoc.getElementById('sn-floating-dropdown');
    if (!d) return;
    isOpen = !isOpen;
    if (isOpen) {{
      var iframe = window.frameElement;
      var rect   = iframe.getBoundingClientRect();
      d.style.position  = 'fixed';
      d.style.top       = (rect.bottom + 8) + 'px';
      d.style.right     = (parentDoc.documentElement.clientWidth - rect.right) + 'px';
      d.style.left      = 'auto';
      d.style.animation = 'snFadeIn 0.15s ease';
      d.style.display   = 'block';
    }} else {{
      d.style.display = 'none';
    }}
  }});
</script>
</body>
</html>""", height=60, scrolling=False)

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

    # ⭐ סרגל עליון — חייב להיות ראשון ⭐
    render_topbar(img_b64, w_text, w_city, greeting)

    # ── פעמון נוטיפיקציות — מוצב מיד אחרי הסרגל ──────────
    today_reminders = st.session_state.rem_live[
        pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today
    ]
    render_notification_bell(today_reminders)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPIs ────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

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
                st.markdown('<p style="text-align: right; color: gray;">אין משימות חדשות.</p>', unsafe_allow_html=True


                            
    
        # ============================
        #      עוזר אישי AI — ורוד
        # ============================

        st.markdown("""
        <div style="
            background:#FADCE6;
            padding:24px;
            border-radius:20px;
            box-shadow:0 8px 22px rgba(225,200,210,0.35);
            direction:rtl;
            text-align:right;
            margin-bottom:20px;
        ">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <span class="material-symbols-rounded" style="font-size:26px;color:#6f5861;">smart_toy</span>
                <h3 style="margin:0;color:#6f5861;">עוזר ה‑AI שלך</h3>
            </div>
            <p style="color:#6f5861;opacity:0.85;margin-top:-5px;">
                שאלי אותי כל דבר על הפרויקטים שלך או צרי משימה חדשה.
            </p>
        </div>
        """, unsafe_allow_html=True)

       
        sel_p = st.selectbox(
            "",
            ["כללי - כל הפרויקטים"] + projects["project_name"].tolist(),
            key="ai_p"
        )
    
        q_in = st.text_area(
            "",
            placeholder="איך אוכל לעזור?",
            key="ai_i",
            height=130
        )
    
        send = st.button("שגר שאילתה 🚀", use_container_width=True)
    
        # לוגיקת שליחה (נשארת כמו שיש לך)
        if send and q_in:
            ...
        
        # הצגת תשובה
        if st.session_state.get("ai_response"):
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
                                
