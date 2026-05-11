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

    if project_name:
        df = df[df["project_name"] == project_name]

    insights_df = load_insights()
    today = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).date()

    st.markdown("""
    <style>
    .side-box {
        background:#ffffff; border-radius:16px; border:1px solid #F4F4F5;
        padding:18px; box-shadow:0 2px 20px rgba(225,200,210,0.15); margin-bottom:14px;
        direction: rtl;
    }
    .ai-insight-box {
        background: #fdf2f8; border: 1.5px solid #FADCE6; border-radius: 12px;
        padding: 12px 16px; margin-top: 8px; font-size: 0.82rem; color: #4e4447;
        line-height: 1.6; direction: rtl; text-align: right;
    }
    .risk-table-header {
        display: grid;
        grid-template-columns: 2fr 1fr 0.7fr 0.7fr 0.8fr 1fr;
        gap: 8px;
        padding: 10px 16px;
        background: #f8fafc;
        border-radius: 10px;
        margin-bottom: 6px;
        direction: rtl;
        text-align: right;
    }
    .risk-table-row {
        display: grid;
        grid-template-columns: 2fr 1fr 0.7fr 0.7fr 0.8fr 1fr;
        gap: 8px;
        padding: 12px 16px;
        border-bottom: 1px solid #f4f4f5;
        direction: rtl;
        text-align: right;
        align-items: center;
    }
    .risk-table-row:hover { background: #fdf6f9; border-radius: 8px; }
    .risk-badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-critical { background:#fef2f2; color:#ef4444; }
    .badge-high     { background:#fffbeb; color:#f59e0b; }
    .badge-medium   { background:#fdf2f8; color:#6f5861; }
    .badge-low      { background:#f8fafc; color:#94a3b8; }
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
        # ── גרף בועות ──
        with st.container(border=True):
            st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:4px;text-align:right;'>מפת סיכונים</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:0.75rem;color:#a1a1aa;margin-bottom:12px;text-align:right;'>הסתברות מול השפעה — גודל הבועה = רמת הסיכון</div>", unsafe_allow_html=True)

            # בניית SVG
            df_active = df[df["status"] != "סגור"].copy()
            df_active["score"] = df_active["probability"] * df_active["impact"]

            svg_width = 500
            svg_height = 300
            pad = 40

            dots_svg = ""
            for _, row in df_active.iterrows():
                color, label = get_risk_color(row["probability"], row["impact"])
                x = pad + ((row["probability"] - 1) / 4) * (svg_width - 2 * pad)
                y = svg_height - pad - ((row["impact"] - 1) / 4) * (svg_height - 2 * pad)
                r = 8 + row["score"] * 1.2
                title_short = str(row["risk_title"])[:20]
                dots_svg += f"""
                <circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{color}" opacity="0.75" stroke="white" stroke-width="2">
                    <title>{row['risk_title']}</title>
                </circle>
                <text x="{x:.0f}" y="{y + r + 12:.0f}" text-anchor="middle" font-size="9" fill="#3f3f46" font-family="Plus Jakarta Sans">{title_short}</text>
                """

            st.markdown(f"""
            <svg width="100%" viewBox="0 0 {svg_width} {svg_height}" style="direction:ltr;">
                <!-- רקע אזורים -->
                <rect x="{pad}" y="{pad}" width="{(svg_width-2*pad)*0.6:.0f}" height="{(svg_height-2*pad)*0.6:.0f}" fill="#fef2f2" opacity="0.5" rx="4"/>
                <rect x="{pad}" y="{pad + (svg_height-2*pad)*0.6:.0f}" width="{(svg_width-2*pad)*0.6:.0f}" height="{(svg_height-2*pad)*0.4:.0f}" fill="#fef9c3" opacity="0.5" rx="4"/>
                <rect x="{pad + (svg_width-2*pad)*0.6:.0f}" y="{pad}" width="{(svg_width-2*pad)*0.4:.0f}" height="{svg_height-2*pad:.0f}" fill="#f0fdf4" opacity="0.5" rx="4"/>
                <!-- קווי רשת -->
                <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{svg_height-pad}" stroke="#e2e8f0" stroke-width="1"/>
                <line x1="{pad}" y1="{svg_height-pad}" x2="{svg_width-pad}" y2="{svg_height-pad}" stroke="#e2e8f0" stroke-width="1"/>
                <!-- ציר X תוויות -->
                <text x="{pad}" y="{svg_height-10}" text-anchor="middle" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">1</text>
                <text x="{pad + (svg_width-2*pad)*0.25:.0f}" y="{svg_height-10}" text-anchor="middle" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">2</text>
                <text x="{pad + (svg_width-2*pad)*0.5:.0f}" y="{svg_height-10}" text-anchor="middle" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">3</text>
                <text x="{pad + (svg_width-2*pad)*0.75:.0f}" y="{svg_height-10}" text-anchor="middle" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">4</text>
                <text x="{svg_width-pad}" y="{svg_height-10}" text-anchor="middle" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">5</text>
                <!-- ציר Y תוויות -->
                <text x="{pad-8}" y="{svg_height-pad}" text-anchor="end" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">1</text>
                <text x="{pad-8}" y="{svg_height-pad-(svg_height-2*pad)*0.25:.0f}" text-anchor="end" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">2</text>
                <text x="{pad-8}" y="{svg_height-pad-(svg_height-2*pad)*0.5:.0f}" text-anchor="end" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">3</text>
                <text x="{pad-8}" y="{svg_height-pad-(svg_height-2*pad)*0.75:.0f}" text-anchor="end" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">4</text>
                <text x="{pad-8}" y="{pad}" text-anchor="end" font-size="10" fill="#a1a1aa" font-family="Plus Jakarta Sans">5</text>
                <!-- כותרות צירים -->
                <text x="{svg_width/2:.0f}" y="{svg_height-2}" text-anchor="middle" font-size="10" fill="#71717A" font-family="Plus Jakarta Sans" font-weight="600">הסתברות ←</text>
                <text x="12" y="{svg_height/2:.0f}" text-anchor="middle" font-size="10" fill="#71717A" font-family="Plus Jakarta Sans" font-weight="600" transform="rotate(-90, 12, {svg_height/2:.0f})">↑ השפעה</text>
                {dots_svg}
            </svg>
            <div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;justify-content:flex-end;">
                <span style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#ef4444;"><span style="width:10px;height:10px;border-radius:50%;background:#ef4444;display:inline-block;opacity:0.75;"></span>קריטי</span>
                <span style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#f59e0b;"><span style="width:10px;height:10px;border-radius:50%;background:#f59e0b;display:inline-block;opacity:0.75;"></span>גבוה</span>
                <span style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#6f5861;"><span style="width:10px;height:10px;border-radius:50%;background:#6f5861;display:inline-block;opacity:0.75;"></span>בינוני</span>
                <span style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#94a3b8;"><span style="width:10px;height:10px;border-radius:50%;background:#94a3b8;display:inline-block;opacity:0.75;"></span>נמוך</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

        # ── טבלת סיכונים ──
        st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:8px;text-align:right;'>פירוט סיכונים</div>", unsafe_allow_html=True)

        fc1, fc2 = st.columns(2)
        with fc1:
            sel_cat = st.selectbox("קטגוריה", ["הכל"] + sorted(df["category"].unique().tolist()), label_visibility="collapsed", key="risk_cat_filter")
        with fc2:
            sel_status = st.selectbox("סטטוס", ["הכל", "פתוח", "בטיפול", "סגור"], label_visibility="collapsed", key="risk_status_filter")

        filtered = df.copy()
        if sel_cat != "הכל":
            filtered = filtered[filtered["category"] == sel_cat]
        if sel_status != "הכל":
            filtered = filtered[filtered["status"] == sel_status]
        filtered["score"] = filtered["probability"] * filtered["impact"]
        filtered = filtered.sort_values("score", ascending=False)

        with st.container(border=True):
            st.markdown("""
            <div class="risk-table-header">
                <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">סיכון</span>
                <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">קטגוריה</span>
                <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">הסתברות</span>
                <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">השפעה</span>
                <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">סטטוס</span>
                <span style="font-size:0.75rem;font-weight:700;color:#94a3b8;">רמה</span>
            </div>
            """, unsafe_allow_html=True)

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
                <div class="risk-table-row">
                    <span style="font-size:0.82rem;font-weight:600;color:#3f3f46;">{row['risk_title']}</span>
                    <span style="font-size:0.78rem;color:#71717A;">{row['category']}</span>
                    <span style="font-size:0.82rem;font-weight:600;color:#3f3f46;text-align:center;">{row['probability']}/5</span>
                    <span style="font-size:0.82rem;font-weight:600;color:#3f3f46;text-align:center;">{row['impact']}/5</span>
                    <span style="font-size:0.78rem;color:#71717A;">{row['status']}</span>
                    <span class="risk-badge {badge_cls}">{label}</span>
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

                btn_label = "🔄 עדכן AI" if saved_insight else "✦ נתח AI"
                if st.button(btn_label, key=f"ai_btn_{card_key}"):
                    with st.spinner("מנתח..."):
                        insight = get_ai_insight(row, df)
                        save_insight(row["project_name"], row["risk_title"], insight)
                        insights_df = load_insights()
                        st.rerun()

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

            st.markdown("""
            <div class="side-box">
                <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:10px;">דדליינים קרובים</div>
            """, unsafe_allow_html=True)

            for _, row in upcoming.iterrows():
                color, _ = get_risk_color(row["probability"], row["impact"])
                days_left = (row["due_date_parsed"].date() - today).days
                days_txt = "עבר!" if days_left < 0 else "היום!" if days_left == 0 else f"{days_left}י'"
                txt_color = "#ef4444" if days_left <= 7 else "#71717A"
                title_short = row['risk_title'][:25] + ("..." if len(row['risk_title']) > 25 else "")
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #f4f4f5;direction:rtl;">
                    <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:0.75rem;font-weight:600;color:#3f3f46;">{title_short}</div>
                    </div>
                    <div style="font-size:0.68rem;font-weight:700;color:{txt_color};white-space:nowrap;">{days_txt}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        except:
            pass

        # ── סיכום קטגוריות ──
        st.markdown("""
        <div class="side-box">
            <div style="font-size:0.95rem;font-weight:700;color:#3f3f46;margin-bottom:12px;">לפי קטגוריה</div>
        """, unsafe_allow_html=True)

        cat_summary = df.groupby("category").apply(
            lambda x: pd.Series({
                "total": len(x),
                "avg_score": (x["probability"] * x["impact"]).mean()
            })
        ).reset_index().sort_values("avg_score", ascending=False)

        for _, row in cat_summary.iterrows():
            bar_pct = min(int((row["avg_score"] / 25) * 100), 100)
            bar_color = "#ef4444" if row["avg_score"] >= 15 else "#f59e0b" if row["avg_score"] >= 9 else "#6f5861"
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:3px;direction:rtl;">
                    <span style="font-weight:600;color:#3f3f46;">{row['category']}</span>
                    <span style="color:#a1a1aa;">{int(row['total'])}</span>
                </div>
                <div style="height:5px;background:#f4f4f5;border-radius:4px;overflow:hidden;">
                    <div style="height:100%;width:{bar_pct}%;background:{bar_color};border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
