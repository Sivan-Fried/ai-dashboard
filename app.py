import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import time
import urllib.parse
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components
import google.generativeai as genai
from streamlit_js_eval import get_geolocation
from openai import OpenAI


# =========================================================
# 1. הגדרות דף ועיצוב (CSS)
# =========================================================
st.set_page_config(layout="wide", page_title="Dashboard Sivan", initial_sidebar_state="collapsed")

st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)

def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# CSS
st.markdown("""
<style>
    .stApp { background-color: #f2f4f7 !important; direction: rtl !important; }
    button[data-baseweb="tab"] { gap: 20px !important; margin-left: 15px !important; padding-right: 20px !important; padding-left: 20px !important; }
    iframe[title="streamlit_js_eval.streamlit_js_eval"] { display: none !important; }
    .dashboard-header { background: linear-gradient(90deg, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-size: 2.2rem; font-weight: 800; margin-bottom: 20px; }
    h3 { font-size: 1.15rem; font-weight: 700; margin-bottom: 12px; color: #1f2a44; text-align: right; }
    .profile-img { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; object-position: center 25%; border: 4px solid white; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .kpi-card { background: white; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .kpi-card b { font-size: 1.4rem; color: #1f2a44; display: block; }
    .record-row { background: white; padding: 10px 15px; border-radius: 10px; margin-bottom: 3px; border: 1px solid #edf2f7; border-right: 5px solid #4facfe; display: flex; justify-content: space-between; align-items: center; direction: rtl; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .tag-blue { color: #4facfe; font-size: 0.8em; font-weight: 600; background: #f0f9ff; padding: 2px 8px; border-radius: 5px; }
    .tag-orange { color: #d97706; font-size: 0.8em; font-weight: 600; background: #fffbeb; padding: 2px 8px; border-radius: 5px; }
    .time-label { color: #64748b; font-size: 0.85em; font-weight: 500; font-family: monospace; }
    .weather-float { display: inline-flex; flex-direction: column; align-items: center; background: white; padding: 8px 15px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #edf2f7; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. פונקציות עזר
# =========================================================

def get_weather_realtime(location):
    if location and 'coords' in location:
        lat, lon = location['coords']['latitude'], location['coords']['longitude']
        try:
            g = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}",
                headers={'User-Agent': 'SivanDash'}
            ).json()
            city = g.get('address', {}).get('city') or g.get('address', {}).get('town') or "ישראל"

            w = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            ).json()
            temp = round(w['current_weather']['temperature'])

            hour = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).hour
            icon = "🌙" if (hour >= 19 or hour < 6) else "☀️"

            return f"{icon} {temp}°C", city
        except:
            pass
    return "☀️ --°C", "ישראל"

def get_azure_tasks():
    ORG_NAME = "amandigital"
    wiql_url = f"https://dev.azure.com/{ORG_NAME}/_apis/wit/wiql?api-version=6.0"
    query = {"query": "SELECT [System.Id], [System.Title], [System.TeamProject], [System.CreatedDate] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] = 'New' ORDER BY [System.ChangedDate] DESC"}
    try:
        auth = ('', st.secrets["AZURE_PAT"])
        res = requests.post(wiql_url, json=query, auth=auth)
        ids = ",".join([str(item['id']) for item in res.json().get('workItems', [])[:5]])
        if not ids:
            return []
        details = requests.get(
            f"https://dev.azure.com/{ORG_NAME}/_apis/wit/workitems?ids={ids}&fields=System.Title,System.TeamProject,System.CreatedDate&api-version=6.0",
            auth=auth
        )
        return details.json().get('value', [])
    except:
        return []

def get_fathom_meetings():
    api_key = st.secrets["FATHOM_API_KEY"]
    url = "https://api.fathom.ai/external/v1/meetings"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('items', [])[:5], 200
        return [], response.status_code
    except:
        return [], 500

def get_fathom_summary(recording_id):
    api_key = st.secrets["FATHOM_API_KEY"]
    url = f"https://api.fathom.ai/external/v1/recordings/{recording_id}/summary"
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("summary", {}).get("markdown_formatted")
        return None
    except:
        return None

def refine_with_ai(raw_text):
    try:
        client = OpenAI()
        prompt = f"סכם את הפגישה לעברית עסקית רהוטה:\n\n{raw_text}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return "שגיאה בסיכום"

def fmt_time(t):
    try:
        return t.strftime("%H:%M")
    except:
        return ""

# =========================================================
# 3. Gemini – זיהוי מודל אוטומטי
# =========================================================

def detect_gemini_model():
    """
    מנסה מודלים לפי סדר עדיפות עד שמוצא מודל זמין עם quota.
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro-latest",
        "gemini-1.0-pro",
        "gemini-pro"
    ]

    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content("ping")
            if hasattr(resp, "text"):
                return model_name
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue
            continue

    return None


# =========================================================
# 4. בניית קונטקסט לפרויקט
# =========================================================

def build_project_context(project_name, projects_df, meetings_df, reminders_df, fathom_state):
    """
    מרכיב קונטקסט טקסטואלי עשיר על פרויקט מסוים מכל הדאטה במערכת.
    """
    parts = []

    # פרטי פרויקט
    proj_rows = projects_df[projects_df["project_name"] == project_name]
    if not proj_rows.empty:
        row = proj_rows.iloc[0]
        parts.append("### פרטי פרויקט")
        parts.append(f"שם פרויקט: {row.get('project_name', '')}")
        parts.append(f"סטטוס: {row.get('status', '')}")
        if "project_type" in row:
            parts.append(f"סוג פרויקט: {row.get('project_type', '')}")

        for col in proj_rows.columns:
            if col not in ["project_name", "status", "project_type"] and pd.notna(row.get(col)):
                parts.append(f"{col}: {row.get(col)}")

    # פגישות
    if "project_name" in meetings_df.columns:
        m_rows = meetings_df[meetings_df["project_name"] == project_name]
        if not m_rows.empty:
            parts.append("\n### פגישות קשורות")
            for _, r in m_rows.iterrows():
                parts.append(
                    f"- פגישה: {r.get('meeting_title','')} | תאריך: {r.get('date','')} | שעות: {r.get('start_time','')}-{r.get('end_time','')}"
                )

    # תזכורות
    if "project_name" in reminders_df.columns:
        r_rows = reminders_df[reminders_df["project_name"] == project_name]
        if not r_rows.empty:
            parts.append("\n### תזכורות")
            for _, r in r_rows.iterrows():
                parts.append(f"- {r.get('date','')}: {r.get('reminder_text','')}")

    # סיכומי Fathom
    fathom_summaries = [
        val.strip()
        for key, val in fathom_state.items()
        if isinstance(key, str) and key.startswith("sum_v4_") and isinstance(val, str) and val.strip()
    ]

    if fathom_summaries:
        parts.append("\n### סיכומי פגישות (Fathom + AI)")
        for idx, s in enumerate(fathom_summaries, start=1):
            parts.append(f"\nסיכום {idx}:\n{s}")

    if not parts:
        return "אין מידע זמין על הפרויקט מעבר לשמו."

    return "\n".join(parts)


# =========================================================
# 5. סוכן AI – ניתוח פרויקט ושאלה חופשית
# =========================================================

def run_project_agent(project_name, question, projects_df, meetings_df, reminders_df):
    """
    סוכן AI: מקבל שם פרויקט ושאלה חופשית, מרכיב קונטקסט, בוחר מודל זמין ומחזיר תשובה.
    """
    model_name = detect_gemini_model()
    if not model_name:
        return "❗ לא נמצא מודל Gemini זמין בחשבון שלך."

    try:
        context = build_project_context(
            project_name=project_name,
            projects_df=projects_df,
            meetings_df=meetings_df,
            reminders_df=reminders_df,
            fathom_state=st.session_state
        )

        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(model_name)

        prompt = f"""
את סוכן ניהול פרויקטים חכם.
הנה כל המידע שיש על הפרויקט "{project_name}":

----------------
{context}
----------------

השאלה:
{question}

ענה בעברית עסקית, בצורה ברורה ותמציתית, עם כותרות קצרות ונקודות עיקריות.
אם משהו לא מופיע במידע – ציין זאת במפורש ואל תמציא.
"""

        resp = model.generate_content(prompt)
        return resp.text if hasattr(resp, "text") else "לא התקבלה תשובה מהמודל."

    except Exception as e:
        return f"שגיאה בהרצת הסוכן על המודל {model_name}: {e}"

# =========================================================
# 6. טעינת נתונים מהקבצים
# =========================================================

try:
    projects = pd.read_excel("my_projects.xlsx")
    meetings = pd.read_excel("meetings.xlsx")
    reminders_df = pd.read_excel("reminders.xlsx")
    today = pd.Timestamp.today().date()
except:
    st.error("Missing Files (my_projects.xlsx, meetings.xlsx, reminders.xlsx)")
    st.stop()


# =========================================================
# 7. Session State – משתנים גלובליים
# =========================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

if "rem_live" not in st.session_state:
    st.session_state.rem_live = reminders_df

if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""

if "adding_reminder" not in st.session_state:
    st.session_state.adding_reminder = False


# =========================================================
# 8. ניהול ניווט לפי פרמטרים ב‑URL
# =========================================================

params = st.query_params

if "proj" in params:
    st.session_state.selected_project = params["proj"]
    st.session_state.current_page = "project"

# =========================================================
# 9. קבלת מיקום מהדפדפן
# =========================================================

loc = get_geolocation()


# =========================================================
# 10. דף פרויקט ספציפי
# =========================================================

if st.session_state.current_page == "project":

    p_name = st.session_state.get("selected_project", "פרויקט")
    st.markdown(f'<h1 class="dashboard-header">{p_name}</h1>', unsafe_allow_html=True)

    if st.button("⬅️ חזרה לדשבורד"):
        st.query_params.clear()
        st.session_state.current_page = "main"
        st.rerun()

    with st.container(border=True):
        st.markdown(f"### ℹ️ ניהול פרויקט: {p_name}")

        tab_work, tab_res, tab_risk, tab_meetings = st.tabs([
            "📅 תוכנית עבודה",
            "👥 משאבים",
            "⚠️ סיכונים",
            "📝 סיכומים"
        ])

        with tab_work:
            if p_name == "אלטשולר שחם":
                exec(open("altshuler_module.py").read())
            else:
                st.info(f"תוכנית עבודה עבור {p_name} בטעינה...")

        with tab_res:
            st.write("רשימת צוות ומשאבים")

        with tab_risk:
            st.write("ניהול סיכונים")

        with tab_meetings:
            st.write("סיכומי פגישות הפרויקט")



# =========================================================
# 11. דף ראשי – Dashboard
# =========================================================

else:

    # =========================================================
    # 11.1 מזג אוויר
    # =========================================================
    if loc:
        w_text, w_city = get_weather_realtime(loc)
    else:
        w_text, w_city = "☀️ --°C", "מזהה מיקום..."

    st.markdown('<h1 class="dashboard-header">Dashboard AI</h1>', unsafe_allow_html=True)

    # =========================================================
    # 11.2 אזור פרופיל
    # =========================================================
    img_b64 = get_base64_image("profile.png")
    now = datetime.datetime.now(ZoneInfo("Asia/Jerusalem"))
    greeting = (
        "בוקר טוב" if 5 <= now.hour < 12 else
        "צהריים טובים" if 12 <= now.hour < 18 else
        "ערב טוב"
    )

    p1, p2, p3 = st.columns([1, 1, 2])

    with p2:
        if img_b64:
            st.markdown(
                f'<div style="display:flex; justify-content:center;">'
                f'<img src="data:image/png;base64,{img_b64}" class="profile-img"></div>',
                unsafe_allow_html=True
            )

    with p3:
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 style='margin-bottom:0;'>{greeting}, סיון!</h3>
                    <p style='color:gray;'>{now.strftime('%d/%m/%Y | %H:%M')}</p>
                </div>
                <div class="weather-float">
                    <div style="font-size: 0.7rem; color: #4facfe; font-weight: 700;">{w_city}</div>
                    <div style="font-size: 1.1rem; color: #1f2a44; font-weight: 800;">{w_text}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    # =========================================================
    # 11.3 KPI – סטטוסים של פרויקטים
    # =========================================================
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f'<div class="kpi-card">בסיכון 🔴<br><b>{len(projects[projects["status"]=="אדום"])}</b></div>',
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card">במעקב 🟡<br><b>{len(projects[projects["status"]=="צהוב"])}</b></div>',
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card">תקין 🟢<br><b>{len(projects[projects["status"]=="ירוק"])}</b></div>',
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card">סה"כ פרויקטים<br><b>{len(projects)}</b></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)


    # =========================================================
    # 11.4 חלוקה לשני טורים
    # =========================================================
    col_right, col_left = st.columns([1, 1])


    # =========================================================
    # 11.5 טור ימין – פרויקטים, משימות, AI אישי
    # =========================================================
    with col_right:

        # ------------------ פרויקטים ------------------
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
                                <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">chevron_left</span>
                            </div>
                        </a>
                    ''', unsafe_allow_html=True)

        # ------------------ משימות אז'ור ------------------
        with st.container(border=True):
            st.markdown('<h3>📋 משימות חדשות באז\'ור</h3>', unsafe_allow_html=True)

            tasks_data = get_azure_tasks()
            if tasks_data:
                for t in tasks_data:
                    f = t.get('fields', {})
                    t_id = t.get('id')
                    t_title = f.get('System.Title', '')
                    p_task = f.get('System.TeamProject', 'General')
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

        # ------------------ עוזר AI אישי ------------------
        with st.container(border=True):
            st.markdown("### ✨ עוזר AI אישי")

            a1, a2 = st.columns([1, 2])

            sel_p = a1.selectbox(
                "פרויקט",
                projects["project_name"].tolist(),
                label_visibility="collapsed",
                key="ai_p"
            )

            q_in = a2.text_input(
                "שאלה",
                placeholder="מה תרצי לדעת? אפשר לשאול על סטטוס, סיכונים, משימות, פגישות ועוד.",
                label_visibility="collapsed",
                key="ai_i"
            )

            if st.button("שגר שאילתה 🚀", use_container_width=True):
                if q_in:
                    with st.spinner("מנתח..."):
                    client = OpenAI()
                    prompt = f"שאלה על פרויקט {sel_p}:\n{q_in}"
                    response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                    )
                    st.session_state.ai_response = response.choices[0].message.content

            if st.session_state.ai_response:
                st.info(st.session_state.ai_response)


    # =========================================================
    # 11.6 טור שמאל – פגישות, תזכורות, Fathom
    # =========================================================
    with col_left:

        # ------------------ פגישות היום ------------------
        with st.container(border=True):
            st.markdown("### 📅 פגישות היום")

            t_m = meetings[pd.to_datetime(meetings["date"]).dt.date == today]

            if t_m.empty:
                st.write("אין פגישות היום")
            else:
                for _, r in t_m.iterrows():
                    s_t = fmt_time(r.get('start_time', ''))
                    e_t = fmt_time(r.get('end_time', ''))

                    st.markdown(
                        f'<div class="record-row">'
                        f'<span style="flex-grow:1; text-align:right;">📌 {r["meeting_title"]}</span>'
                        f'<span class="time-label">{s_t}-{e_t}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        # ------------------ תזכורות ------------------
        with st.container(border=True):
            st.markdown("### 🔔 תזכורות")

            t_r = st.session_state.rem_live[
                pd.to_datetime(st.session_state.rem_live["date"]).dt.date == today
            ]

            if not t_r.empty:
                for _, row in t_r.iterrows():
                    st.markdown(
                        f'<div class="record-row">'
                        f'<span>🔔 {row["reminder_text"]}</span>'
                        f'<span class="tag-orange">{row.get("project_name", "כללי")}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.write("אין תזכורות להיום.")

            # הוספת תזכורת
            if st.session_state.adding_reminder:
                with st.container():
                    r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 3, 0.5, 0.5])

                    with r_col1:
                        new_proj = st.selectbox(
                            "פרויקט",
                            projects["project_name"].tolist() + ["כללי"],
                            label_visibility="collapsed",
                            key="new_rem_proj"
                        )

                    with r_col2:
                        new_text = st.text_input(
                            "תיאור",
                            placeholder="מה להזכיר?",
                            label_visibility="collapsed",
                            key="new_rem_text"
                        )

                    with r_col3:
                        if st.button("✅", key="save_rem_btn"):
                            if new_text:
                                new_row = {
                                    "date": today,
                                    "reminder_text": new_text,
                                    "project_name": new_proj
                                }
                                st.session_state.rem_live = pd.concat(
                                    [st.session_state.rem_live, pd.DataFrame([new_row])],
                                    ignore_index=True
                                )
                                st.session_state.adding_reminder = False
                                st.rerun()

                    with r_col4:
                        if st.button("❌", key="cancel_rem_btn"):
                            st.session_state.adding_reminder = False
                            st.rerun()

            else:
                if st.button("➕ הוספת תזכורת", use_container_width=True):
                    st.session_state.adding_reminder = True
                    st.rerun()

        # ------------------ Fathom ------------------
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
                    except:
                        pass

            if 'fathom_meetings' not in st.session_state:
                try:
                    items, status = get_fathom_meetings()
                    st.session_state['fathom_meetings'] = items if status == 200 else []
                except:
                    st.session_state['fathom_meetings'] = []

            # כאן אפשר להוסיף UI להצגת הפגישות
            for m in st.session_state['fathom_meetings']:
                st.markdown(
                    f'<div class="record-row">'
                    f'<span>🎤 {m.get("title", "פגישה")}</span>'
                    f'<span class="time-label">{m.get("created_at", "")}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
