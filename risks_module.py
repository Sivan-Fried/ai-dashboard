# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
import re
import google.generativeai as genai
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

INSIGHTS_FILE = "risks_ai_insights.xlsx"

def load_risks():
    try:
        return pd.read_excel("risks.xlsx")
    except Exception as e:
        st.error(f"שגיאה בטעינת קובץ סיכונים: {e}")
        return pd.DataFrame()

def load_insights():
    try:
        return pd.read_excel(INSIGHTS_FILE)
    except:
        return pd.DataFrame(columns=["project_name", "risk_title", "insight", "created_at"])

def save_insight(project_name, risk_title, insight_text):
    new_row = {
        "project_name": project_name,
        "risk_title": risk_title,
        "insight": insight_text,
        "created_at": datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d/%m/%Y %H:%M")
    }
    try:
        existing = pd.read_excel(INSIGHTS_FILE)
        mask = (existing["project_name"] == project_name) & (existing["risk_title"] == risk_title)
        if mask.any():
            existing.loc[mask, "insight"] = insight_text
            existing.loc[mask, "created_at"] = new_row["created_at"]
            updated = existing
        else:
            updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
    except:
        updated = pd.DataFrame([new_row])
    updated.to_excel(INSIGHTS_FILE, index=False)
    
    # שמירה ל-GitHub
    try:
        import requests, base64
        token = st.secrets["GITHUB_TOKEN"]
        repo = "Sivan-Fried/ai-dashboard"
        branch = "main"
        path = INSIGHTS_FILE
        
        with open(INSIGHTS_FILE, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        
        payload = {
            "message": f"Update AI insights - {project_name}",
            "content": content,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha
            
        requests.put(url, json=payload, headers=headers)
    except Exception as e:
        st.warning(f"לא ניתן לשמור ל-GitHub: {str(e)}")

def get_risk_color(probability, impact):
    score = probability * impact
    if score >= 15:
        return "#ef4444", "קריטי"
    elif score >= 9:
        return "#f59e0b", "גבוה"
    elif score >= 4:
        return "#6f5861", "בינוני"
    else:
        return "#94a3b8", "נמוך"

def show_risks_page(project_name=None):
    df = load_risks()
    if df.empty:
        st.error("לא נמצא קובץ risks.xlsx")
        return

    if project_name:
        df = df[df["project_name"] == project_name]

    insights_df = load_insights()

    st.markdown("""
    <style>
    .risk-header {
        display:grid;
        grid-template-columns:2.5fr 1fr 0.7fr 0.7fr 0.7fr 0.8fr;
        gap:8px; padding:10px 16px;
        background:#f8fafc; border-radius:10px;
        margin-bottom:4px; direction:rtl; text-align:right;
    }
    .risk-row {
        display:grid;
        grid-template-columns:2.5fr 1fr 0.7fr 0.7fr 0.7fr 0.8fr;
        gap:8px; padding:12px 16px;
        border-bottom:1px solid #f4f4f5;
        direction:rtl; text-align:right; align-items:center;
    }
    .risk-row:hover { background:#fdf6f9; border-radius:8px; }
    .r-badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .r-badge-critical { background:#fef2f2; color:#ef4444; }
    .r-badge-high     { background:#fffbeb; color:#f59e0b; }
    .r-badge-medium   { background:#fdf2f8; color:#6f5861; }
    .r-badge-low      { background:#f8fafc; color:#94a3b8; }
    .st-key-ai_risks_container {
        background-color: #fadce6 !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: none !important;
    }
    .st-key-ai_risks_send button {
        background-color: #9ca3af !important;
        border: none !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        color: #ffffff !important;
        font-size: 1.3rem !important;
    }
    .st-key-ai_risks_send button p {
        color: #ffffff !important;
    }
    .st-key-ai_risks_send {
        display: flex !important;
        justify-content: flex-end !important;
        margin-top: 8px !important;
    }
    .st-key-close_analysis_hidden {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    div.element-container:has(.fathom-row-ui) + div.element-container {
        margin-top: -45px !important;
        margin-bottom: 0px !important;
    }
    div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-right: 5px solid transparent !important;
        width: 100% !important;
        height: 45px !important;
        color: transparent !important;
        z-index: 20;
    }
    div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button:hover {
        background: transparent !important;
        box-shadow: none !important;
        transform: none !important;
    }
    div.element-container:has(.fathom-row-ui):has(+ div.element-container div[data-testid="stButton"] button:hover) .fathom-row-ui {
        border-right-color: #f0b8cb !important;
        background-color: #fdf6f9 !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # כותרת
    title = f"ניהול סיכונים — {project_name}" if project_name else "ניהול סיכונים"
    st.markdown(f"### {title}", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.82rem;color:#a1a1aa;margin-top:-4px;text-align:right;padding-right:18px;'>מעקב, ניתוח וניהול סיכונים</p>", unsafe_allow_html=True)

    # חישובים
    df["score"] = df["probability"] * df["impact"]
    critical_risks = len(df[df["score"] >= 15])
    high_risks     = len(df[(df["score"] >= 9) & (df["score"] < 15)])
    medium_risks   = len(df[(df["score"] >= 4) & (df["score"] < 9)])
    low_risks      = len(df[df["score"] < 4])

    active_df = df[df["status"] != "סגור"]
    total_score = active_df["score"].mean() if not active_df.empty else 0
    pct = min(int((total_score / 25) * 100), 100)
    r = 26
    circ = 2 * 3.14159 * r
    offset = circ * (1 - pct / 100)
    gauge_color = "#ef4444" if pct >= 60 else "#f59e0b" if pct >= 35 else "#10b981"
    gauge_label = "גבוה" if pct >= 60 else "בינוני" if pct >= 35 else "נמוך"

    # KPIs
    k0, k1, k2, k3, k4 = st.columns(5)

    with k0:
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fef2f2;">
                    <span class="material-symbols-rounded" style="color:#ef4444;">crisis_alert</span>
                </div>
                <span class="kpi-badge" style="background:#fef2f2;color:#ef4444;">קריטי</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{critical_risks}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)

    with k1:
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fffbeb;">
                    <span class="material-symbols-rounded" style="color:#f59e0b;">warning</span>
                </div>
                <span class="kpi-badge" style="background:#fffbeb;color:#f59e0b;">גבוה</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{high_risks}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)

    with k2:
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fdf2f8;">
                    <span class="material-symbols-rounded" style="color:#6f5861;">info</span>
                </div>
                <span class="kpi-badge" style="background:#fdf2f8;color:#6f5861;">בינוני</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{medium_risks}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)

    with k3:
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#f8fafc;">
                    <span class="material-symbols-rounded" style="color:#94a3b8;">check_circle</span>
                </div>
                <span class="kpi-badge" style="background:#f8fafc;color:#94a3b8;">נמוך</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{low_risks}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-container" style="text-align:center;align-items:center;">
            <div style="font-size:0.75rem;font-weight:700;color:#3f3f46;margin-bottom:4px;">מד סיכון כולל</div>
            <svg width="75" height="75" viewBox="0 0 60 60" style="display:block;margin:0 auto;">
                <circle cx="30" cy="30" r="{r}" fill="none" stroke="#f4f4f5" stroke-width="6"/>
                <circle cx="30" cy="30" r="{r}" fill="none" stroke="{gauge_color}"
                    stroke-width="6" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
                    stroke-linecap="round" transform="rotate(-90 30 30)"/>
                <text x="30" y="27" text-anchor="middle" font-size="11" font-weight="800" fill="{gauge_color}" font-family="Plus Jakarta Sans">{pct}%</text>
                <text x="30" y="40" text-anchor="middle" font-size="8" fill="{gauge_color}" font-family="Plus Jakarta Sans" font-weight="700">{gauge_label}</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # טבלת סיכונים
    st.markdown("### פירוט סיכונים", unsafe_allow_html=True)

    filtered = df.copy().sort_values("score", ascending=False)

    with st.container(border=True):
        st.markdown("""
        <div class="risk-header">
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">סיכון</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">קטגוריה</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">הסתברות</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">השפעה</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">סיכון משוקלל</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">רמה</span>
        </div>
        """, unsafe_allow_html=True)

        for _, row in filtered.iterrows():
            color, label = get_risk_color(row["probability"], row["impact"])
            badge_map = {"קריטי": "r-badge-critical", "גבוה": "r-badge-high", "בינוני": "r-badge-medium", "נמוך": "r-badge-low"}
            badge_cls = badge_map.get(label, "r-badge-low")
            st.markdown(f"""
            <div class="risk-row">
                <span style="font-size:0.82rem;font-weight:600;color:#3f3f46;">{row['risk_title']}</span>
                <span style="font-size:0.78rem;color:#71717A;">{row['category']}</span>
                <span style="font-size:0.82rem;color:#3f3f46;">{row['probability']}</span>
                <span style="font-size:0.82rem;color:#3f3f46;">{row['impact']}</span>
                <span style="font-size:0.82rem;font-weight:700;color:#3f3f46;">{int(row['score'])}</span>
                <span class="r-badge {badge_cls}">{label}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # תחתית
    col_right, col_left = st.columns([1, 1])

    with col_right:
        top3 = active_df.sort_values("score", ascending=False).head(3)
        st.markdown("### דורשים טיפול עכשיו", unsafe_allow_html=True)
        with st.container(border=True):
            for i, (_, row) in enumerate(top3.iterrows()):
                color, label = get_risk_color(row["probability"], row["impact"])
                badge_map = {"קריטי": "r-badge-critical", "גבוה": "r-badge-high", "בינוני": "r-badge-medium", "נמוך": "r-badge-low"}
                badge_cls = badge_map.get(label, "r-badge-low")
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:1px solid #f4f4f5;direction:rtl;text-align:right;">
                    <div style="width:24px;height:24px;border-radius:50%;background:#94a3b8;color:white;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:800;flex-shrink:0;">{i+1}</div>
                    <div style="flex:1;">
                        <div style="font-size:0.82rem;font-weight:600;color:#3f3f46;margin-bottom:2px;">{row['risk_title']}</div>
                        <div style="font-size:0.7rem;color:#a1a1aa;">{row['category']} · ציון {int(row['score'])}/25</div>
                    </div>
                    <span class="r-badge {badge_cls}">{label}</span>
                </div>
                """, unsafe_allow_html=True)

    with col_left:
        saved_analysis = None
        analysis_date = ""
        if not insights_df.empty:
            mask = (insights_df["project_name"] == (project_name or "כללי")) & \
                   (insights_df["risk_title"] == "__full_analysis__")
            if mask.any():
                saved_analysis = insights_df[mask].iloc[0]["insight"]
                analysis_date = insights_df[mask].iloc[0]["created_at"]

        st.markdown("### ניתוח AI כולל", unsafe_allow_html=True)

        with st.container(border=True, key="ai_risks_container"):
            st.markdown("""
            <div style="background:white;border-radius:16px;padding:16px 20px;margin-bottom:12px;">
                <div style="font-size:0.82rem;color:#71717A;text-align:right;">
                    ניתוח מעמיק של כל הסיכונים עם המלצות מעשיות
                </div>
            </div>
            """, unsafe_allow_html=True)

            open_key = f"analysis_open_{project_name}"
            is_open = st.session_state.get(open_key, False)

            # כפתור ניתוח תמיד מוצג
            col_empty, col_btn = st.columns([0.89, 0.11])
            with col_btn:
                send = st.button("↩", key="ai_risks_send", use_container_width=True)
            force = st.session_state.pop(f"force_rerun_{project_name}", False)
            if send or force:
                with st.spinner("מנתח..."):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-2.5-flash-lite')
                        risks_text = "\n".join([
                            f"- {r['risk_title']} | הסתברות {r['probability']}/5 | השפעה {r['impact']}/5 | {r['category']} | {r.get('notes','')}"
                            for _, r in df.iterrows()
                        ])
                        prompt = f"""אתה יועץ ניהול סיכונים בכיר. נתח את כל הסיכונים של הפרויקט "{project_name}" ותן דוח מסכם קצר בעברית עסקית:

סיכונים:
{risks_text}

1. **תמונת מצב** — משפט אחד
2. **3 סיכונים דחופים** — ומדוע
3. **דפוסים** — קשרים בין הסיכונים
4. **המלצות מיידיות** — 2-3 פעולות

היה תמציתי."""
                        response = model.generate_content(prompt)
                        save_insight(project_name or "כללי", "__full_analysis__", response.text)
                        st.session_state[open_key] = True
                        st.rerun()
                    except Exception as e:
                        if saved_analysis:
                            st.info("לא ניתן לעדכן כעת — מציג ניתוח קודם")
                        else:
                            st.error(f"שגיאה: {str(e)}")

            if saved_analysis:
                arrow = "&#8249;" if is_open else "&#8250;"
                st.markdown(f"""
                <div class="fathom-row-ui" style="font-size:0.92rem; font-weight:normal;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span class="material-symbols-outlined" style="font-size:18px;color:#64748b;transform:scale(0.8);">smart_toy</span>
                        <span style="font-size:0.88rem;">ניתוח AI — {analysis_date}</span>
                    </div>
                    <div></div>
                    <span style="color:#94a3b8;font-size:22px;line-height:1;flex-shrink:0;margin-right:8px;">{arrow}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("", key=f"toggle_analysis_{project_name}", use_container_width=True):
                    st.session_state[open_key] = not is_open
                    st.rerun()

                if is_open:
                    import html as html_module
                    escaped = html_module.escape(saved_analysis)
                    formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
                    formatted = re.sub(r'^#{1,3} (.+)$', r'<h3 class="ai-response-heading">\1</h3>', formatted, flags=re.MULTILINE)
                    formatted = re.sub(r'^- (.+)$', r'<li class="ai-response-li">\1</li>', formatted, flags=re.MULTILINE)
                    formatted = formatted.replace('\n', '<br>')
                    components.html(f"""<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="utf-8"/>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet"/>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: transparent; direction: rtl; }}
.ai-response-card {{ background: #ffffff; border: 1.5px solid #FADCE6; border-radius: 16px; padding: 20px 24px; direction: rtl; }}
.ai-response-topbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid #fdf0f5; }}
.ai-response-label {{ display: flex; align-items: center; gap: 8px; font-size: 0.82rem; font-weight: 700; color: #6f5861; }}
.ai-response-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #10b981; }}
.ai-response-actions {{ display: flex; gap: 6px; }}
.ai-action-btn {{ background: #fdf2f8; border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.2s; }}
.ai-action-btn:hover {{ background: #FADCE6; }}
.ai-action-btn .material-symbols-outlined {{ font-size: 16px; color: #64748b; font-family: 'Material Symbols Outlined'; -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased; }}
.ai-response-body {{ font-size: 0.9rem; color: #4e4447; line-height: 1.75; text-align: right; }}
.ai-response-heading {{ font-size: 1rem; font-weight: 700; color: #3f3f46; margin: 14px 0 6px 0; }}
.ai-response-li {{ color: #4e4447; margin-bottom: 4px; list-style: none; padding-right: 14px; position: relative; display: block; }}
.ai-response-li::before {{ content: '●'; color: #f0b8cb; position: absolute; right: 0; font-size: 10px; top: 4px; }}
</style>
</head>
<body>
<div class="ai-response-card">
<div class="ai-response-topbar">
    <div class="ai-response-label">
        <span class="material-symbols-outlined" style="font-size:18px; color:#64748b;">smart_toy</span>
        <div class="ai-response-dot"></div>
    </div>
    <div class="ai-response-actions">
        <button class="ai-action-btn" id="risks-copy-btn" title="העתק">
            <span class="material-symbols-outlined">content_copy</span>
        </button>
        <button class="ai-action-btn" id="risks-share-btn" title="שתף">
            <span class="material-symbols-outlined">share</span>
        </button>
    </div>
</div>
<div class="ai-response-body" id="risks-response-text">{formatted}</div>
</div>
<script>
document.getElementById('risks-copy-btn').addEventListener('click', function() {{
    var text = document.getElementById('risks-response-text').innerText;
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.focus(); ta.select();
    try {{
        document.execCommand('copy');
        var btn = document.getElementById('risks-copy-btn');
        btn.querySelector('span').innerText = 'check';
        setTimeout(function() {{ btn.querySelector('span').innerText = 'content_copy'; }}, 1500);
    }} catch(e) {{}}
    document.body.removeChild(ta);
}});
document.getElementById('risks-share-btn').addEventListener('click', function() {{
    var text = document.getElementById('risks-response-text').innerText;
    if (navigator.share) {{ navigator.share({{text: text}}); }}
}});
</script>
</body>
</html>""", height=600, scrolling=True)
