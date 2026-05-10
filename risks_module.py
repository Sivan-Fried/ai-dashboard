# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
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

def get_ai_insight(risk_row, all_risks_df):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        project_risks = all_risks_df[all_risks_df["project_name"] == risk_row["project_name"]]
        other_risks = "\n".join([
            f"- {r['risk_title']} (הסתברות {r['probability']}, השפעה {r['impact']})"
            for _, r in project_risks.iterrows()
            if r["risk_title"] != risk_row["risk_title"]
        ])
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

def show_risks_page(project_name=None):
    df = load_risks()
    if df.empty:
        st.error("לא נמצא קובץ risks.xlsx")
        return

    insights_df = load_insights()
    today = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).date()

    st.markdown("""
    <style>
    .risk-card {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #F4F4F5;
        border-right: 4px solid #FADCE6;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 12px rgba(225,200,210,0.12);
        direction: rtl;
        transition: all 0.2s ease;
    }
    .risk-card:hover { border-right-color: #f0b8cb; box-shadow: 0 4px 20px rgba(225,200,210,0.25); }
    .risk-badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-critical { background:#fef2f2; color:#ef4444; }
    .badge-high     { background:#fffbeb; color:#f59e0b; }
    .badge-medium   { background:#fdf2f8; color:#6f5861; }
    .badge-low      { background:#f8fafc; color:#94a3b8; }
    .ai-insight-box {
        background: #fdf2f8; border: 1.5px solid #FADCE6; border-radius: 12px;
        padding: 12px 16px; margin-top: 8px; font-size: 0.82rem; color: #4e4447;
        line-height: 1.6; direction: rtl;
    }
    .matrix-cell {
        border-radius: 8px; display:flex; align-items:center; justify-content:center;
        font-size:0.65rem; font-weight:600; min-height:48px; text-align:center; padding:4px;
        margin-bottom:4px;
    }
    .side-box {
        background:#ffffff; border-radius:16px; border:1px solid #F4F4F5;
        padding:18px; box-shadow:0 2px 20px rgba(225,200,210,0.15); margin-bottom:14px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── כותרת ──
    st.markdown("""
    <div style="margin-bottom:20px;">
        <h2 style="font-size:1.5rem;font-weight:800;color:#3f3f46;margin:0;">
            <span style="color:#f0b8cb;">⬥</span> ניהול סיכונים
        </h2>
        <p style="font-size:0.82rem;color:#a1a1aa;margin:4px 0 0 0;">מעקב, ניתוח וניהול סיכונים בכל הפרויקטים</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──
    open_risks     = len(df[df["status"] == "פתוח"])
    critical_risks = len(df[(df["probability"] * df["impact"]) >= 15])
    in_progress    = len(df[df["status"] == "בטיפול"])
    closed         = len(df[df["status"] == "סגור"])

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

    col_main, col_side = st.columns([2, 1])

    with col_main:
        # ── מטריצה ──
        with st.container(border=True):
            st.markdown("### <span class='material-symbols-outlined' style='vertical-align:middle;font-size:1.2rem;color:#64748b;margin-left:6px;'>grid_on</span> מטריצת סיכונים", unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.78rem;color:#a1a1aa;margin-top:-8px;margin-bottom:12px;'>הסתברות (עמודות) מול השפעה (שורות)</p>", unsafe_allow_html=True)

            matrix_data = {}
            for _, row in df[df["status"] != "סגור"].iterrows():
                key = (int(row["probability"]), int(row["impact"]))
                if key not in matrix_data:
                    matrix_data[key] = []
                matrix_data[key].append(row["project_name"][:8])

            cols_m = st.columns([0.12] + [1]*5)
            with cols_m[0]:
                st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
                for impact in range(5, 0, -1):
                    st.markdown(f"<div style='height:52px;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#71717A;'>{impact}</div>", unsafe_allow_html=True)

            for prob in range(1, 6):
                with cols_m[prob]:
                    st.markdown(f"<div style='height:32px;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#71717A;'>{prob}</div>", unsafe_allow_html=True)
                    for impact in range(5, 0, -1):
                        score = prob * impact
                        if score >= 15:
                            bg, bc = "#fee2e2", "#ef4444"
                        elif score >= 9:
                            bg, bc = "#fef9c3", "#f59e0b"
                        elif score >= 4:
                            bg, bc = "#fdf2f8", "#FADCE6"
                        else:
                            bg, bc = "#f8fafc", "#e2e8f0"

                        items = matrix_data.get((prob, impact), [])
                        content = "<br>".join(items) if items else f"<span style='color:#e2e8f0;font-size:0.6rem;'>{score}</span>"
                        dot = f"<span style='width:6px;height:6px;border-radius:50%;background:{bc};display:inline-block;margin-left:3px;flex-shrink:0;'></span>" if items else ""

                        st.markdown(f"""<div class="matrix-cell" style="background:{bg};border:1px solid {bc};">
                            {dot}<span style="line-height:1.2;">{content}</span></div>""", unsafe_allow_html=True)

            st.markdown("""
            <div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;">
                <span style="font-size:0.7rem;color:#71717A;">עמודות = הסתברות (1-5)</span>
                <span style="font-size:0.7rem;color:#71717A;">שורות = השפעה (1-5)</span>
                <span style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#ef4444;"><span style="width:8px;height:8px;border-radius:50%;background:#ef4444;display:inline-block;"></span>קריטי (15+)</span>
                <span style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#f59e0b;"><span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;display:inline-block;"></span>גבוה (9-14)</span>
                <span style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#6f5861;"><span style="width:8px;height:8px;border-radius:50%;background:#FADCE6;display:inline-block;"></span>בינוני (4-8)</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

        # ── פירוט סיכונים ──
        st.markdown("### <span class='material-symbols-outlined' style='vertical-align:middle;font-size:1.2rem;color:#64748b;margin-left:6px;'>list</span> פירוט סיכונים", unsafe_allow_html=True)

        fc1, fc2 = st.columns(2)
        with fc1:
            sel_project = st.selectbox("פרויקט", ["הכל"] + sorted(df["project_name"].unique().tolist()), label_visibility="collapsed", key="risk_proj_filter")
        with fc2:
            sel_cat = st.selectbox("קטגוריה", ["הכל"] + sorted(df["category"].unique().tolist()), label_visibility="collapsed", key="risk_cat_filter")

        filtered = df.copy()
        if sel_project != "הכל":
            filtered = filtered[filtered["project_name"] == sel_project]
        if sel_cat != "הכל":
            filtered = filtered[filtered["category"] == sel_cat]

        filtered["score"] = filtered["probability"] * filtered["impact"]
        filtered = filtered.sort_values("score", ascending=False)

        with st.container(border=True):
            for _, row in filtered.iterrows():
                color, label = get_risk_color(row["probability"], row["impact"])
                badge_map = {"קריטי": "badge-critical", "גבוה": "badge-high", "בינוני": "badge-medium", "נמוך": "badge-low"}
                badge_cls = badge_map.get(label, "badge-low")
                card_key = f"risk_{row['project_name']}_{row['risk_title']}".replace(" ", "_").replace("/", "_")

                saved_insight = None
                created_at = ""
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
                        <span class="risk-badge {badge_cls}">{label}</span>
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
                        <span style="font-size:0.7rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">{row['project_name']}</span>
                        <span style="font-size:0.7rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">{row['category']}</span>
                        <span style="font-size:0.7rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">הסתברות: {row['probability']}/5 · השפעה: {row['impact']}/5</span>
                        <span style="font-size:0.7rem;color:#71717A;background:#f8fafc;padding:2px 8px;border-radius:20px;">{row['status']}</span>
                    </div>
                    <div style="font-size:0.8rem;color:#94a3b8;">{row.get('notes','')}</div>
                </div>
                """, unsafe_allow_html=True)

                if saved_insight:
                    import re
                    formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', saved_insight)
                    formatted = formatted.replace('\n', '<br>')
                    st.markdown(f"""
                    <div class="ai-insight-box">
                        <div style="display:flex;align-items:center;gap:8px;font-size:0.72rem;font-weight:700;color:#6f5861;margin-bottom:8px;">
                            <span class="material-symbols-outlined" style="font-size:16px;color:#6f5861;">smart_toy</span>
                            <span style="width:8px;height:8px;border-radius:50%;background:#10b981;display:inline-block;"></span>
                            ניתוח AI — נשמר ב-{created_at}
                        </div>
                        {formatted}
                    </div>
                    """, unsafe_allow_html=True)

                btn_label = "🔄 עדכן ניתוח AI" if saved_insight else "✦ נתח עם AI"
                if st.button(btn_label, key=f"ai_btn_{card_key}"):
                    with st.spinner("מנתח..."):
                        insight = get_ai_insight(row, df)
                        save_insight(row["project_name"], row["risk_title"], insight)
                        st.session_state[f"insight_{card_key}"] = insight

    with col_side:
        # ── מד סיכון ──
        active_df = df[df["status"] != "סגור"]
        total_score = (active_df["probability"] * active_df["impact"]).mean() if not active_df.empty else 0
        pct = min(int((total_score / 25) * 100), 100)
        dash = 2 * 3.14159 * 54
        offset = dash * (1 - pct / 100)
        gauge_color = "#ef4444" if pct >= 60 else "#f59e0b" if pct >= 35 else "#10b981"
        gauge_label = "גבוה" if pct >= 60 else "בינוני" if pct >= 35 else "נמוך"

        st.markdown(f"""
        <div class="side-box" style="text-align:center;">
            <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:12px;">מד סיכון כולל</div>
            <svg width="120" height="120" viewBox="0 0 120 120" style="display:block;margin:0 auto;">
                <circle cx="60" cy="60" r="54" fill="none" stroke="#f4f4f5" stroke-width="10"/>
                <circle cx="60" cy="60" r="54" fill="none" stroke="{gauge_color}"
                    stroke-width="10" stroke-dasharray="{dash:.1f}" stroke-dashoffset="{offset:.1f}"
                    stroke-linecap="round" transform="rotate(-90 60 60)"/>
                <text x="60" y="56" text-anchor="middle" font-size="20" font-weight="800" fill="{gauge_color}" font-family="Plus Jakarta Sans">{pct}%</text>
                <text x="60" y="72" text-anchor="middle" font-size="9" fill="#a1a1aa" font-family="Plus Jakarta Sans">רמת סיכון</text>
            </svg>
            <div style="font-size:0.75rem;color:{gauge_color};font-weight:600;margin-top:6px;">{gauge_label}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── ציר זמן ──
        try:
            upcoming = df[df["status"] != "סגור"].copy()
            upcoming["due_date_parsed"] = pd.to_datetime(upcoming["due_date"], format="%d/%m/%Y", errors="coerce")
            upcoming = upcoming.dropna(subset=["due_date_parsed"]).sort_values("due_date_parsed").head(7)

            timeline_items = ""
            for _, row in upcoming.iterrows():
                color, _ = get_risk_color(row["probability"], row["impact"])
                days_left = (row["due_date_parsed"].date() - today).days
                days_txt = "עבר!" if days_left < 0 else "היום!" if days_left == 0 else f"{days_left}י'"
                txt_color = "#ef4444" if days_left <= 7 else "#71717A"
                title_short = row['risk_title'][:25] + ("..." if len(row['risk_title']) > 25 else "")
                timeline_items += f"""
                <div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #f4f4f5;direction:rtl;">
                    <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:0.75rem;font-weight:600;color:#3f3f46;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{title_short}</div>
                        <div style="font-size:0.68rem;color:#a1a1aa;">{row['project_name']}</div>
                    </div>
                    <div style="font-size:0.68rem;font-weight:700;color:{txt_color};white-space:nowrap;">{days_txt}</div>
                </div>"""

            st.markdown(f"""
            <div class="side-box">
                <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:10px;">דדליינים קרובים</div>
                {timeline_items}
            </div>
            """, unsafe_allow_html=True)
        except:
            pass

        # ── לפי פרויקט ──
        proj_summary = df.groupby("project_name").apply(
            lambda x: pd.Series({
                "total": len(x),
                "critical": len(x[(x["probability"] * x["impact"]) >= 15]),
                "avg_score": (x["probability"] * x["impact"]).mean()
            })
        ).reset_index().sort_values("avg_score", ascending=False)

        proj_bars = ""
        for _, row in proj_summary.iterrows():
            bar_pct = min(int((row["avg_score"] / 25) * 100), 100)
            bar_color = "#ef4444" if row["critical"] > 0 else "#f59e0b" if row["avg_score"] >= 9 else "#6f5861"
            proj_bars += f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:3px;">
                    <span style="font-weight:600;color:#3f3f46;">{row['project_name']}</span>
                    <span style="color:#a1a1aa;">{int(row['total'])}</span>
                </div>
                <div style="height:5px;background:#f4f4f5;border-radius:4px;overflow:hidden;">
                    <div style="height:100%;width:{bar_pct}%;background:{bar_color};border-radius:4px;"></div>
                </div>
            </div>"""

        st.markdown(f"""
        <div class="side-box">
            <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:12px;">לפי פרויקט</div>
            {proj_bars}
        </div>
        """, unsafe_allow_html=True)
