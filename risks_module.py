# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
import re
import google.generativeai as genai
from zoneinfo import ZoneInfo

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
    .white-box {
        background:#ffffff;
        border-radius:16px;
        border:1px solid #F4F4F5;
        padding:18px;
        box-shadow:0 2px 20px rgba(225,200,210,0.15);
        margin-bottom:14px;
        direction:rtl;
        text-align:right;
    }
    .box-title {
        font-size:0.95rem;
        font-weight:700;
        color:#3f3f46;
        margin-bottom:12px;
        direction:rtl;
        text-align:right;
    }
    .risk-header {
        display:grid;
        grid-template-columns:2.5fr 1fr 0.7fr 0.7fr 0.8fr;
        gap:8px;
        padding:10px 16px;
        background:#f8fafc;
        border-radius:10px;
        margin-bottom:4px;
        direction:rtl;
        text-align:right;
    }
    .risk-row {
        display:grid;
        grid-template-columns:2.5fr 1fr 0.7fr 0.7fr 0.8fr;
        gap:8px;
        padding:12px 16px;
        border-bottom:1px solid #f4f4f5;
        direction:rtl;
        text-align:right;
        align-items:center;
    }
    .risk-row:hover { background:#fdf6f9; border-radius:8px; }
    .badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-critical { background:#fef2f2; color:#ef4444; }
    .badge-high     { background:#fffbeb; color:#f59e0b; }
    .badge-medium   { background:#fdf2f8; color:#6f5861; }
    .badge-low      { background:#f8fafc; color:#94a3b8; }
    .filter-label {
        font-size:0.75rem;
        font-weight:600;
        color:#94a3b8;
        margin-bottom:4px;
        text-align:right;
        direction:rtl;
    }
    .ai-response-card {
        background: #ffffff;
        border: 1.5px solid #FADCE6;
        border-radius: 16px;
        padding: 20px 24px;
        direction: rtl;
        margin-top: 8px;
    }
    .ai-response-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        padding-bottom: 12px;
        border-bottom: 1px solid #fdf0f5;
    }
    .ai-response-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        color: #6f5861;
    }
    .ai-response-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        display: inline-block;
    }
    .ai-response-body {
        font-size: 0.88rem;
        color: #4e4447;
        line-height: 1.75;
        text-align: right;
        direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── כותרת ──
    title = f"ניהול סיכונים — {project_name}" if project_name else "ניהול סיכונים"
    st.markdown(f"""
    <div style="margin-bottom:20px;direction:rtl;text-align:right;">
        <h2 style="font-size:1.5rem;font-weight:800;color:#3f3f46;margin:0;">
            <span style="color:#f0b8cb;">⬥</span> {title}
        </h2>
        <p style="font-size:0.82rem;color:#a1a1aa;margin:4px 0 0 0;">מעקב, ניתוח וניהול סיכונים</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs — מד סיכון בשמאל + 4 KPIs ──
    active_df = df[df["status"] != "סגור"]
    total_score = (active_df["probability"] * active_df["impact"]).mean() if not active_df.empty else 0
    pct = min(int((total_score / 25) * 100), 100)
    r = 34
    circ = 2 * 3.14159 * r
    offset = circ * (1 - pct / 100)
    gauge_color = "#ef4444" if pct >= 60 else "#f59e0b" if pct >= 35 else "#10b981"
    gauge_label = "גבוה" if pct >= 60 else "בינוני" if pct >= 35 else "נמוך"

    open_risks     = len(df[df["status"] == "פתוח"])
    critical_risks = len(df[(df["probability"] * df["impact"]) >= 15])
    in_progress    = len(df[df["status"] == "בטיפול"])
    closed         = len(df[df["status"] == "סגור"])

    k4, k3, k2, k1, k0 = st.columns(5)

    with k0:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fef2f2;"><span class="material-symbols-rounded" style="color:#ef4444;">crisis_alert</span></div>
                <span class="kpi-badge" style="background:#fef2f2;color:#ef4444;">קריטי</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{critical_risks}</span>
            </div></div></div>''', unsafe_allow_html=True)

    with k1:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fffbeb;"><span class="material-symbols-rounded" style="color:#f59e0b;">warning</span></div>
                <span class="kpi-badge" style="background:#fffbeb;color:#f59e0b;">פתוח</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{open_risks}</span>
            </div></div></div>''', unsafe_allow_html=True)

    with k2:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#eff6ff;"><span class="material-symbols-rounded" style="color:#60a5fa;">pending</span></div>
                <span class="kpi-badge" style="background:#eff6ff;color:#3b82f6;">בטיפול</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{in_progress}</span>
            </div></div></div>''', unsafe_allow_html=True)

    with k3:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#ecfdf5;"><span class="material-symbols-rounded" style="color:#34d399;">check_circle</span></div>
                <span class="kpi-badge" style="background:#ecfdf5;color:#10b981;">סגור</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{closed}</span>
            </div></div></div>''', unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-container" style="text-align:center;align-items:center;justify-content:center;">
            <div style="font-size:0.82rem;font-weight:700;color:#3f3f46;margin-bottom:6px;text-align:center;">מד סיכון</div>
            <svg width="80" height="80" viewBox="0 0 80 80" style="display:block;margin:0 auto;">
                <circle cx="40" cy="40" r="{r}" fill="none" stroke="#f4f4f5" stroke-width="8"/>
                <circle cx="40" cy="40" r="{r}" fill="none" stroke="{gauge_color}"
                    stroke-width="8" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
                    stroke-linecap="round" transform="rotate(-90 40 40)"/>
                <text x="40" y="37" text-anchor="middle" font-size="15" font-weight="800" fill="{gauge_color}" font-family="Plus Jakarta Sans">{pct}%</text>
                <text x="40" y="52" text-anchor="middle" font-size="8" fill="#71717A" font-family="Plus Jakarta Sans" font-weight="600">{gauge_label}</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── טבלת סיכונים — רוחב מלא ──
    st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:8px;text-align:right;'>פירוט סיכונים</div>", unsafe_allow_html=True)

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown('<div class="filter-label">סוג</div>', unsafe_allow_html=True)
        categories = ["הכל"] + sorted(df["category"].unique().tolist())
        sel_cat = st.selectbox("סוג", categories, label_visibility="collapsed", key="risk_cat_filter")
    with fc2:
        st.markdown('<div class="filter-label">סטטוס</div>', unsafe_allow_html=True)
        statuses = ["הכל"] + sorted(df["status"].unique().tolist())
        sel_status = st.selectbox("סטטוס", statuses, label_visibility="collapsed", key="risk_status_filter")

    filtered = df.copy()
    if sel_cat != "הכל":
        filtered = filtered[filtered["category"] == sel_cat]
    if sel_status != "הכל":
        filtered = filtered[filtered["status"] == sel_status]
    filtered["score"] = filtered["probability"] * filtered["impact"]
    filtered = filtered.sort_values("score", ascending=False)

    with st.container(border=True):
        st.markdown("""
        <div class="risk-header">
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">סיכון</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">קטגוריה</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">הסתברות</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">השפעה</span>
            <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">רמה</span>
        </div>
        """, unsafe_allow_html=True)

        for _, row in filtered.iterrows():
            color, label = get_risk_color(row["probability"], row["impact"])
            badge_map = {"קריטי": "badge-critical", "גבוה": "badge-high", "בינוני": "badge-medium", "נמוך": "badge-low"}
            badge_cls = badge_map.get(label, "badge-low")
            st.markdown(f"""
            <div class="risk-row">
                <span style="font-size:0.82rem;font-weight:600;color:#3f3f46;">{row['risk_title']}</span>
                <span style="font-size:0.78rem;color:#71717A;">{row['category']}</span>
                <span style="font-size:0.82rem;color:#3f3f46;">{row['probability']}/5</span>
                <span style="font-size:0.82rem;color:#3f3f46;">{row['impact']}/5</span>
                <span class="badge {badge_cls}">{label}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── תחתית — שתי עמודות ──
    col_right, col_left = st.columns([1, 1])

    with col_right:
        top3 = active_df.copy()
        top3["score"] = top3["probability"] * top3["impact"]
        top3 = top3.sort_values("score", ascending=False).head(3)

        st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:10px;text-align:right;'>🚨 דורשים טיפול עכשיו</div>", unsafe_allow_html=True)
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        for i, (_, row) in enumerate(top3.iterrows()):
            color, label = get_risk_color(row["probability"], row["impact"])
            badge_map = {"קריטי": "badge-critical", "גבוה": "badge-high", "בינוני": "badge-medium", "נמוך": "badge-low"}
            badge_cls = badge_map.get(label, "badge-low")
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:1px solid #f4f4f5;direction:rtl;text-align:right;">
                <div style="width:24px;height:24px;border-radius:50%;background:#94a3b8;color:white;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:800;flex-shrink:0;">{i+1}</div>
                <div style="flex:1;">
                    <div style="font-size:0.82rem;font-weight:600;color:#3f3f46;margin-bottom:2px;">{row['risk_title']}</div>
                    <div style="font-size:0.7rem;color:#a1a1aa;">{row['category']} · ציון {int(row['score'])}/25</div>
                </div>
                <span class="badge {badge_cls}">{label}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_left:
        saved_analysis = None
        analysis_date = ""
        if not insights_df.empty:
            mask = (insights_df["project_name"] == (project_name or "כללי")) & \
                   (insights_df["risk_title"] == "__full_analysis__")
            if mask.any():
                saved_analysis = insights_df[mask].iloc[0]["insight"]
                analysis_date = insights_df[mask].iloc[0]["created_at"]

        if saved_analysis:
            formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', saved_analysis)
            formatted = re.sub(r'^#{1,3} (.+)$', r'<h4 style="color:#3f3f46;margin:10px 0 4px 0;">\1</h4>', formatted, flags=re.MULTILINE)
            formatted = re.sub(r'^- (.+)$', r'<li style="margin-bottom:4px;">\1</li>', formatted, flags=re.MULTILINE)
            formatted = formatted.replace('\n', '<br>')
            st.markdown(f"""
            <div class="ai-response-card">
                <div class="ai-response-topbar">
                    <div class="ai-response-label">
                        <span class="material-symbols-outlined" style="font-size:18px;color:#64748b;">smart_toy</span>
                        <span class="ai-response-dot"></span>
                        ניתוח AI כולל
                    </div>
                    <span style="font-size:0.7rem;color:#a1a1aa;">נשמר ב-{analysis_date}</span>
                </div>
                <div class="ai-response-body">{formatted}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="white-box" style="text-align:center;padding:30px;">
                <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:8px;">✦ ניתוח AI כולל</div>
                <div style="font-size:0.82rem;color:#a1a1aa;">לחצי על הכפתור לקבלת ניתוח מעמיק של כל הסיכונים עם המלצות מעשיות</div>
            </div>
            """, unsafe_allow_html=True)

        btn_label = "🔄 עדכן ניתוח" if saved_analysis else "✦ נתח את כל הסיכונים עם AI"
        if st.button(btn_label, key="full_ai_analysis", use_container_width=True):
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
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה: {str(e)}")
