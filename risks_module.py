# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
import json
import os
import google.generativeai as genai
import streamlit.components.v1 as components
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

def get_ai_insight(risk_row, all_risks_df):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        project_risks = all_risks_df[all_risks_df["project_name"] == risk_row["project_name"]]
        other_risks = "\n".join([f"- {r['risk_title']} (הסתברות {r['probability']}, השפעה {r['impact']})"
                                  for _, r in project_risks.iterrows()
                                  if r["risk_title"] != risk_row["risk_title"]])

        prompt = f"""אתה יועץ ניהול סיכונים בכיר. נתח את הסיכון הבא ותן המלצות מעשיות.

פרויקט: {risk_row['project_name']}
סיכון: {risk_row['risk_title']}
הסתברות: {risk_row['probability']}/5
השפעה: {risk_row['impact']}/5
קטגוריה: {risk_row['category']}
סטטוס: {risk_row['status']}
הערות: {risk_row.get('notes', '')}

סיכונים נוספים בפרויקט:
{other_risks if other_risks else 'אין'}

תן ניתוח קצר ומעשי בעברית עסקית:
1. **מה הסיכון האמיתי** — משפט אחד
2. **המלצה מיידית** — פעולה אחת קונקרטית
3. **המלצה לטווח ארוך** — פעולה אחת אסטרטגית

היה תמציתי וממוקד. לא יותר מ-5 משפטים סה"כ."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה בניתוח AI: {str(e)}"

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

def render_risk_matrix(df):
    """מרנדר מטריצת סיכונים אינטראקטיבית"""
    dots_js = []
    for _, row in df.iterrows():
        color, label = get_risk_color(row["probability"], row["impact"])
        # המרה מ-1-5 לאחוזים על הצירים
        x = ((row["probability"] - 1) / 4) * 80 + 10
        y = 90 - ((row["impact"] - 1) / 4) * 80
        tooltip = f"{row['project_name']}: {row['risk_title']}"
        dots_js.append(f"""{{x:{x},y:{y},color:"{color}",label:"{label}",tooltip:"{tooltip}"}}""")

    dots_str = "[" + ",".join(dots_js) + "]"

    html = f"""<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="utf-8"/>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: transparent; direction: rtl; }}
.matrix-wrap {{ background: #fff; border-radius: 16px; border: 1px solid #F4F4F5; padding: 20px; box-shadow: 0 2px 20px rgba(225,200,210,0.15); }}
.matrix-title {{ font-size: 1rem; font-weight: 700; color: #3f3f46; margin-bottom: 4px; }}
.matrix-sub {{ font-size: 0.75rem; color: #a1a1aa; margin-bottom: 16px; }}
.matrix-container {{ display: flex; gap: 8px; }}
.y-axis-label {{ writing-mode: vertical-lr; transform: rotate(180deg); font-size: 0.7rem; color: #71717A; display: flex; align-items: center; justify-content: center; width: 20px; }}
.matrix-inner {{ flex: 1; }}
.matrix-svg-wrap {{ position: relative; width: 100%; height: 260px; }}
svg {{ width: 100%; height: 100%; }}
.dot {{ cursor: pointer; transition: r 0.2s; }}
.dot:hover {{ filter: drop-shadow(0 0 6px rgba(0,0,0,0.3)); }}
.tooltip {{ position: absolute; background: #1e293b; color: white; padding: 8px 12px; border-radius: 8px; font-size: 0.75rem; pointer-events: none; display: none; z-index: 100; max-width: 200px; line-height: 1.4; white-space: normal; }}
.x-axis {{ display: flex; justify-content: space-between; margin-top: 4px; padding: 0 20px; }}
.x-axis span {{ font-size: 0.7rem; color: #71717A; }}
.legend {{ display: flex; gap: 16px; margin-top: 12px; flex-wrap: wrap; }}
.legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: #71717A; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
</style>
</head>
<body>
<div class="matrix-wrap">
  <div class="matrix-title">מטריצת סיכונים</div>
  <div class="matrix-sub">הסתברות מול השפעה עסקית — לחצי על נקודה לפרטים</div>
  <div class="matrix-container">
    <div class="y-axis-label">השפעה עסקית</div>
    <div class="matrix-inner">
      <div class="matrix-svg-wrap">
        <svg id="matrix-svg" viewBox="0 0 500 260" preserveAspectRatio="none">
          <!-- רקע מחולק לאזורים -->
          <rect x="0" y="0" width="500" height="260" fill="#fef2f2" rx="8"/>
          <rect x="0" y="87" width="500" height="86" fill="#fefce8"/>
          <rect x="0" y="173" width="500" height="87" fill="#f0fdf4"/>
          <!-- קווי רשת -->
          <line x1="100" y1="0" x2="100" y2="260" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="200" y1="0" x2="200" y2="260" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="300" y1="0" x2="300" y2="260" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="400" y1="0" x2="400" y2="260" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="0" y1="87" x2="500" y2="87" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="0" y1="173" x2="500" y2="173" stroke="#e2e8f0" stroke-width="1"/>
          <!-- תוויות אזורים -->
          <text x="8" y="50" font-size="10" fill="#ef444460" font-family="Plus Jakarta Sans" font-weight="600">קריטי</text>
          <text x="8" y="137" font-size="10" fill="#f59e0b60" font-family="Plus Jakarta Sans" font-weight="600">גבוה</text>
          <text x="8" y="223" font-size="10" fill="#22c55e60" font-family="Plus Jakarta Sans" font-weight="600">נמוך</text>
          <!-- נקודות סיכון -->
          <g id="dots"></g>
        </svg>
        <div class="tooltip" id="tooltip"></div>
      </div>
      <div class="x-axis">
        <span>הסתברות נמוכה</span>
        <span>בינונית</span>
        <span>הסתברות גבוהה</span>
      </div>
      <div class="legend">
        <div class="legend-item"><div class="legend-dot" style="background:#ef4444"></div>קריטי (15+)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div>גבוה (9-14)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#6f5861"></div>בינוני (4-8)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#94a3b8"></div>נמוך (1-3)</div>
      </div>
    </div>
  </div>
</div>
<script>
var dots = {dots_str};
var svg = document.getElementById('dots');
var tooltip = document.getElementById('tooltip');
var svgEl = document.getElementById('matrix-svg');

dots.forEach(function(d) {{
  var cx = (d.x / 100) * 500;
  var cy = (d.y / 100) * 260;
  var circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', cx);
  circle.setAttribute('cy', cy);
  circle.setAttribute('r', 10);
  circle.setAttribute('fill', d.color);
  circle.setAttribute('class', 'dot');
  circle.setAttribute('opacity', '0.85');
  circle.addEventListener('mouseenter', function(e) {{
    circle.setAttribute('r', 14);
    tooltip.style.display = 'block';
    tooltip.textContent = d.tooltip;
  }});
  circle.addEventListener('mousemove', function(e) {{
    var rect = document.querySelector('.matrix-svg-wrap').getBoundingClientRect();
    tooltip.style.left = (e.clientX - rect.left + 10) + 'px';
    tooltip.style.top = (e.clientY - rect.top - 30) + 'px';
  }});
  circle.addEventListener('mouseleave', function() {{
    circle.setAttribute('r', 10);
    tooltip.style.display = 'none';
  }});
  svg.appendChild(circle);
}});
</script>
</body>
</html>"""
    return html


def show_risks_page(project_name=None):
    df = load_risks()
    insights_df = load_insights()

    if df.empty:
        st.error("לא נמצא קובץ risks.xlsx")
        return

    today = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).date()

    # ── CSS ספציפי לדף ──
    st.markdown("""
    <style>
    .risk-card {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #F4F4F5;
        border-right: 4px solid #FADCE6;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(225,200,210,0.12);
        direction: rtl;
    }
    .risk-card:hover {
        border-right-color: #f0b8cb;
        box-shadow: 0 4px 20px rgba(225,200,210,0.25);
    }
    .risk-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .risk-badge-critical { background: #fef2f2; color: #ef4444; }
    .risk-badge-high     { background: #fffbeb; color: #f59e0b; }
    .risk-badge-medium   { background: #fdf2f8; color: #6f5861; }
    .risk-badge-low      { background: #f8fafc; color: #94a3b8; }
    .ai-insight-box {
        background: #fdf2f8;
        border: 1.5px solid #FADCE6;
        border-radius: 12px;
        padding: 12px 16px;
        margin-top: 10px;
        font-size: 0.82rem;
        color: #4e4447;
        line-height: 1.6;
        direction: rtl;
    }
    .ai-insight-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #6f5861;
        margin-bottom: 8px;
    }
    .ai-dot { width:8px; height:8px; border-radius:50%; background:#10b981; display:inline-block; }
    .gauge-wrap {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #F4F4F5;
        padding: 20px;
        box-shadow: 0 2px 20px rgba(225,200,210,0.15);
        text-align: center;
    }
    .timeline-wrap {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #F4F4F5;
        padding: 20px;
        box-shadow: 0 2px 20px rgba(225,200,210,0.15);
    }
    .timeline-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f4f4f5;
        direction: rtl;
    }
    .timeline-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── כותרת ──
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-size:1.6rem; font-weight:800; color:#3f3f46; margin:0;">
            <span style="color:#f0b8cb;">⬥</span> ניהול סיכונים
        </h2>
        <p style="font-size:0.82rem; color:#a1a1aa; margin:4px 0 0 0;">מעקב, ניתוח וניהול סיכונים בכל הפרויקטים</p>
    </div>
    """, unsafe_allow_html=True)

    # ── שורת KPIs ──
    open_risks = len(df[df["status"] == "פתוח"])
    critical_risks = len(df[(df["probability"] * df["impact"]) >= 15])
    in_progress = len(df[df["status"] == "בטיפול"])
    closed = len(df[df["status"] == "סגור"])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fef2f2;"><span class="material-symbols-rounded" style="color:#ef4444;">crisis_alert</span></div>
                <span class="kpi-badge" style="background:#fef2f2;color:#ef4444;">קריטי</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{critical_risks}</span>
            </div></div></div>''', unsafe_allow_html=True)
    with k2:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fffbeb;"><span class="material-symbols-rounded" style="color:#f59e0b;">warning</span></div>
                <span class="kpi-badge" style="background:#fffbeb;color:#f59e0b;">פתוח</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{open_risks}</span>
            </div></div></div>''', unsafe_allow_html=True)
    with k3:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#eff6ff;"><span class="material-symbols-rounded" style="color:#60a5fa;">pending</span></div>
                <span class="kpi-badge" style="background:#eff6ff;color:#3b82f6;">בטיפול</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{in_progress}</span>
            </div></div></div>''', unsafe_allow_html=True)
    with k4:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#ecfdf5;"><span class="material-symbols-rounded" style="color:#34d399;">check_circle</span></div>
                <span class="kpi-badge" style="background:#ecfdf5;color:#10b981;">סגור</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">סיכונים</span><span class="kpi-number">{closed}</span>
            </div></div></div>''', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    # ── שתי עמודות ראשיות ──
    col_main, col_side = st.columns([2, 1])

    with col_main:
        # מטריצה
        matrix_html = render_risk_matrix(df)
        components.html(matrix_html, height=380, scrolling=False)

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

        # פירטור סיכונים
        st.markdown("### <span class='material-symbols-outlined' style='vertical-align:middle;font-size:1.2rem;color:#64748b;margin-left:6px;'>list</span> פירוט סיכונים פעילים", unsafe_allow_html=True)

        # סינון
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            projects_list = ["הכל"] + sorted(df["project_name"].unique().tolist())
            sel_project = st.selectbox("פרויקט", projects_list, label_visibility="collapsed", key="risk_proj_filter")
        with filter_col2:
            categories = ["הכל"] + sorted(df["category"].unique().tolist())
            sel_cat = st.selectbox("קטגוריה", categories, label_visibility="collapsed", key="risk_cat_filter")

        filtered = df.copy()
        if sel_project != "הכל":
            filtered = filtered[filtered["project_name"] == sel_project]
        if sel_cat != "הכל":
            filtered = filtered[filtered["category"] == sel_cat]

        # מיון לפי ציון סיכון
        filtered["score"] = filtered["probability"] * filtered["impact"]
        filtered = filtered.sort_values("score", ascending=False)

        for _, row in filtered.iterrows():
            color, label = get_risk_color(row["probability"], row["impact"])
            badge_class = {"קריטי": "risk-badge-critical", "גבוה": "risk-badge-high",
                          "בינוני": "risk-badge-medium", "נמוך": "risk-badge-low"}.get(label, "risk-badge-low")

            card_key = f"risk_{row['project_name']}_{row['risk_title']}".replace(" ", "_")
            open_key = f"open_{card_key}"

            # בדיקה אם יש insight שמור
            saved_insight = None
            if not insights_df.empty:
                mask = (insights_df["project_name"] == row["project_name"]) & \
                       (insights_df["risk_title"] == row["risk_title"])
                if mask.any():
                    saved_insight = insights_df[mask].iloc[0]["insight"]
                    created_at = insights_df[mask].iloc[0]["created_at"]

            st.markdown(f"""
            <div class="risk-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-size:0.88rem;font-weight:600;color:#3f3f46;">{row['risk_title']}</span>
                    <span class="risk-badge {badge_class}">{label}</span>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
                    <span style="font-size:0.72rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">{row['project_name']}</span>
                    <span style="font-size:0.72rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">{row['category']}</span>
                    <span style="font-size:0.72rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">הסתברות: {row['probability']}/5</span>
                    <span style="font-size:0.72rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">השפעה: {row['impact']}/5</span>
                </div>
                <div style="font-size:0.8rem;color:#71717A;">{row.get('notes','')}</div>
            </div>
            """, unsafe_allow_html=True)

            if saved_insight:
                st.markdown(f"""
                <div class="ai-insight-box">
                    <div class="ai-insight-header">
                        <span class="material-symbols-outlined" style="font-size:16px;color:#6f5861;">smart_toy</span>
                        <span class="ai-dot"></span>
                        ניתוח AI — נשמר ב-{created_at}
                    </div>
                    {saved_insight.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

            btn_label = "🔄 עדכן ניתוח AI" if saved_insight else "✦ נתח עם AI"
            if st.button(btn_label, key=f"ai_btn_{card_key}", use_container_width=False):
                with st.spinner("מנתח..."):
                    insight = get_ai_insight(row, df)
                    save_insight(row["project_name"], row["risk_title"], insight)
                    st.rerun()

    with col_side:
        # מד סיכון כולל
        total_score = df[df["status"] != "סגור"]["probability"].multiply(df[df["status"] != "סגור"]["impact"]).mean()
        max_score = 25
        pct = min(int((total_score / max_score) * 100), 100) if not pd.isna(total_score) else 0
        dash = 2 * 3.14159 * 54
        offset = dash * (1 - pct / 100)

        if pct >= 60:
            gauge_color = "#ef4444"
            gauge_label = "גבוה — דורש תשומת לב"
        elif pct >= 35:
            gauge_color = "#f59e0b"
            gauge_label = "בינוני — דורש ניטור"
        else:
            gauge_color = "#10b981"
            gauge_label = "נמוך — תחת שליטה"

        st.markdown(f"""
        <div class="gauge-wrap">
            <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:16px;">מד סיכון כולל</div>
            <svg width="140" height="140" viewBox="0 0 140 140" style="display:block;margin:0 auto;">
                <circle cx="70" cy="70" r="54" fill="none" stroke="#f4f4f5" stroke-width="12"/>
                <circle cx="70" cy="70" r="54" fill="none" stroke="{gauge_color}"
                    stroke-width="12" stroke-dasharray="{dash:.1f}" stroke-dashoffset="{offset:.1f}"
                    stroke-linecap="round" transform="rotate(-90 70 70)"/>
                <text x="70" y="65" text-anchor="middle" font-size="22" font-weight="800" fill="{gauge_color}" font-family="Plus Jakarta Sans">{pct}%</text>
                <text x="70" y="82" text-anchor="middle" font-size="9" fill="#a1a1aa" font-family="Plus Jakarta Sans">רמת סיכון</text>
            </svg>
            <div style="font-size:0.75rem;color:#71717A;margin-top:8px;">{gauge_label}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

        # ציר זמן סיכונים
        st.markdown("""
        <div class="timeline-wrap">
            <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:16px;">ציר זמן — דדליינים קרובים</div>
        """, unsafe_allow_html=True)

        upcoming = df[df["status"] != "סגור"].copy()
        try:
            upcoming["due_date_parsed"] = pd.to_datetime(upcoming["due_date"], format="%d/%m/%Y", errors="coerce")
            upcoming = upcoming.dropna(subset=["due_date_parsed"])
            upcoming = upcoming.sort_values("due_date_parsed")
            upcoming = upcoming.head(8)

            timeline_html = ""
            for _, row in upcoming.iterrows():
                color, label = get_risk_color(row["probability"], row["impact"])
                due_str = row["due_date_parsed"].strftime("%d/%m/%Y")
                days_left = (row["due_date_parsed"].date() - today).days
                if days_left < 0:
                    days_txt = "עבר"
                elif days_left == 0:
                    days_txt = "היום!"
                elif days_left <= 7:
                    days_txt = f"{days_left} ימים"
                else:
                    days_txt = due_str

                timeline_html += f"""
                <div class="timeline-item">
                    <div class="timeline-dot" style="background:{color};"></div>
                    <div style="flex:1;">
                        <div style="font-size:0.8rem;font-weight:600;color:#3f3f46;">{row['risk_title'][:30]}...</div>
                        <div style="font-size:0.7rem;color:#a1a1aa;">{row['project_name']} · {days_txt}</div>
                    </div>
                </div>"""

            st.markdown(timeline_html + "</div>", unsafe_allow_html=True)
        except:
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

        # סיכום לפי פרויקט
        st.markdown("""
        <div class="timeline-wrap">
            <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:16px;">סיכונים לפי פרויקט</div>
        """, unsafe_allow_html=True)

        proj_summary = df.groupby("project_name").apply(
            lambda x: pd.Series({
                "total": len(x),
                "critical": len(x[(x["probability"] * x["impact"]) >= 15]),
                "avg_score": (x["probability"] * x["impact"]).mean()
            })
        ).reset_index()
        proj_summary = proj_summary.sort_values("avg_score", ascending=False)

        proj_html = ""
        for _, row in proj_summary.iterrows():
            bar_pct = min(int((row["avg_score"] / 25) * 100), 100)
            if row["critical"] > 0:
                bar_color = "#ef4444"
            elif row["avg_score"] >= 9:
                bar_color = "#f59e0b"
            else:
                bar_color = "#6f5861"

            proj_html += f"""
            <div style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#3f3f46;margin-bottom:4px;">
                    <span style="font-weight:600;">{row['project_name']}</span>
                    <span style="color:#a1a1aa;">{row['total']} סיכונים</span>
                </div>
                <div style="height:6px;background:#f4f4f5;border-radius:4px;overflow:hidden;">
                    <div style="height:100%;width:{bar_pct}%;background:{bar_color};border-radius:4px;"></div>
                </div>
            </div>"""

        st.markdown(proj_html + "</div>", unsafe_allow_html=True)
