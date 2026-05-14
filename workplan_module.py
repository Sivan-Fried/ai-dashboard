import pandas as pd
import datetime
import re


def clean_text(x):
    if not isinstance(x, str):
        x = str(x)
    x = x.strip()
    x = re.sub(r'[\u200f\u202b\u202c\u202d\u202e]', '', x)
    x = re.sub(r'[\x00-\x1F\x7F]', '', x)
    return x


def load_workplan_df():
    df = pd.read_excel("work_plans.xlsx")
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")
    df["project_name"] = df["project_name"].apply(clean_text)
    return df


def build_timeline_html(project_name):
    df = load_workplan_df()
    project_name = clean_text(project_name)
    project_df = df[df["project_name"] == project_name].copy()
    project_df = project_df.sort_values("date")

    if project_df.empty:
        return "<div style='text-align:right; font-size:16px; padding:10px;'>אין נתונים עבור הפרויקט</div>"

    today = datetime.date.today()
    today_str = today.strftime("%d.%m")

    # בניית רשימת אבני הדרך
    items_data = []
    for _, row in project_df.iterrows():
        name = str(row["milestone_name"])
        if "עמיתים" in name:
            tag_class = "amit"
        elif "מעסיקים" in name:
            tag_class = "measy"
        elif "סוכנים" in name:
            tag_class = "soch"
        else:
            tag_class = "amit"

        status_val = str(row["status"]).strip()
        status_class = {"LIVE": "live", "WIP": "wip", "HOLD": ""}.get(status_val, "")

        date_str = row["date"].strftime("%d.%m.%Y")
        date_iso = row["date"].strftime("%Y-%m-%d")

        contents = str(row.get("version_contents", "")).strip()
        contents_html = contents.replace("\n", "<br>") if contents and contents != "nan" else ""
        tooltip_html = f"<div class='tooltip'>{contents_html}</div>" if contents_html else ""

        items_data.append({
            "name": name,
            "tag_class": tag_class,
            "status_class": status_class,
            "status_val": status_val,
            "date_str": date_str,
            "date_iso": date_iso,
            "tooltip_html": tooltip_html,
        })

    # בניית HTML לאבני הדרך — חלופי שמאל/ימין
    # אבני דרך באותו תאריך יוצאות מאותה נקודה (זוג)
    items_html_parts = []
    i = 0
    side_counter = 0  # מונה גלובלי לקביעת צד

    while i < len(items_data):
        item = items_data[i]
        # בדיקה אם הפריט הבא באותו תאריך
        same_date_group = [item]
        j = i + 1
        while j < len(items_data) and items_data[j]["date_iso"] == item["date_iso"]:
            same_date_group.append(items_data[j])
            j += 1

        if len(same_date_group) == 2:
            # שניים באותו תאריך — ימין ושמאל מאותה נקודה
            left_item = same_date_group[0]
            right_item = same_date_group[1]

            left_card = f"""
                <div class="card" data-date="{left_item['date_iso']}">
                    {left_item['tooltip_html']}
                    <span class="tag {left_item['tag_class']}">{left_item['name']}</span>
                    <div class="date">{left_item['date_str']}</div>
                    <span class="status {left_item['status_class']}">{left_item['status_val']}</span>
                </div>"""

            right_card = f"""
                <div class="card" data-date="{right_item['date_iso']}">
                    {right_item['tooltip_html']}
                    <span class="tag {right_item['tag_class']}">{right_item['name']}</span>
                    <div class="date">{right_item['date_str']}</div>
                    <span class="status {right_item['status_class']}">{right_item['status_val']}</span>
                </div>"""

            items_html_parts.append(f"""
            <div class="timeline-row paired" data-date="{item['date_iso']}">
                <div class="side left">{left_card}</div>
                <div class="center-col">
                    <div class="dot"></div>
                </div>
                <div class="side right">{right_card}</div>
            </div>""")
            side_counter += 2
        else:
            # אבן דרך יחידה — צד מתחלף
            side = "left" if side_counter % 2 == 0 else "right"
            card = f"""
                <div class="card" data-date="{item['date_iso']}">
                    {item['tooltip_html']}
                    <span class="tag {item['tag_class']}">{item['name']}</span>
                    <div class="date">{item['date_str']}</div>
                    <span class="status {item['status_class']}">{item['status_val']}</span>
                </div>"""

            if side == "left":
                items_html_parts.append(f"""
            <div class="timeline-row single" data-date="{item['date_iso']}">
                <div class="side left">{card}</div>
                <div class="center-col">
                    <div class="dot"></div>
                </div>
                <div class="side right"></div>
            </div>""")
            else:
                items_html_parts.append(f"""
            <div class="timeline-row single" data-date="{item['date_iso']}">
                <div class="side left"></div>
                <div class="center-col">
                    <div class="dot"></div>
                </div>
                <div class="side right">{card}</div>
            </div>""")
            side_counter += 1

        i = j

    items_html = "\n".join(items_html_parts)

    html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@200;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Assistant', sans-serif;
            background-color: white;
            direction: rtl;
            overflow-x: hidden;
        }}

        /* ── כפתורי סינון ── */
        .controls {{
            display: flex;
            justify-content: flex-end;
            padding: 16px 24px 0 24px;
            position: sticky;
            top: 0;
            background: white;
            z-index: 10;
        }}

        .toggle-group {{
            display: flex;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            padding: 4px;
        }}

        .toggle-btn {{
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            font-family: 'Assistant', sans-serif;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            color: #94a3b8;
            background: transparent;
        }}

        .toggle-btn.active {{
            background: #FADCE6;
            color: #63646c;
        }}

        .toggle-btn:hover:not(.active) {{
            color: #475569;
        }}

        /* ── מיכל ציר הזמן ── */
        .timeline-container {{
            position: relative;
            padding: 24px 0 32px 0;
        }}

        /* קו ציר אנכי במרכז */
        .timeline-container::before {{
            content: '';
            position: absolute;
            top: 0;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 2px;
            background: #cbd5e1;
            z-index: 0;
        }}

        /* ── חיווי היום ── */
        .today-marker {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 8px 0;
            z-index: 5;
        }}

        .today-marker::before {{
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            height: 2px;
            background: #FADCE6;
            z-index: 1;
        }}

        .today-badge {{
            background: #FADCE6;
            color: #63646c;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 12px;
            border-radius: 20px;
            position: relative;
            z-index: 2;
            white-space: nowrap;
        }}

        /* ── שורת ציר הזמן ── */
        .timeline-row {{
            display: grid;
            grid-template-columns: 1fr 40px 1fr;
            align-items: center;
            gap: 0;
            margin: 8px 0;
            position: relative;
            z-index: 2;
        }}

        .timeline-row.hidden {{
            display: none !important;
        }}

        /* עמודת מרכז עם נקודה */
        .center-col {{
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            z-index: 3;
        }}

        .dot {{
            width: 12px;
            height: 12px;
            background: #475569;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 0 2px #475569;
            flex-shrink: 0;
        }}

        /* צדדים */
        .side {{
            padding: 4px 12px;
            display: flex;
            align-items: center;
        }}

        .side.left {{
            justify-content: flex-end;
        }}

        .side.right {{
            justify-content: flex-start;
        }}

        /* כרטיס אבן דרך */
        .card {{
            background: white;
            padding: 6px 8px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            border: 1px solid #f1f5f9;
            text-align: center;
            width: 130px;
            position: relative;
            flex-shrink: 0;
        }}

        .card:hover .tooltip {{
            display: block;
        }}

        /* תגית */
        .tag {{
            font-size: 10px;
            font-weight: 700;
            padding: 1px 5px;
            border-radius: 3px;
            display: inline-block;
            margin-bottom: 2px;
            line-height: 1.4;
        }}
        .amit  {{ background: #FADCE6; color: #831843; }}
        .measy {{ background: #eff6ff; color: #1e40af; }}
        .soch  {{ background: #fff7ed; color: #9a3412; }}

        .date {{
            font-size: 12px;
            font-weight: 600;
            color: #1e293b;
            margin: 1px 0;
        }}

        .status {{
            font-size: 9px;
            font-weight: 700;
            margin-top: 1px;
            display: block;
        }}
        .live {{ color: #10b981; }}
        .wip  {{ color: #f59e0b; }}

        /* טולטיפ */
        .tooltip {{
            display: none;
            position: absolute;
            bottom: 110%;
            right: 50%;
            transform: translateX(50%);
            background: #1e293b;
            color: white;
            font-size: 11px;
            line-height: 1.6;
            padding: 8px 12px;
            border-radius: 8px;
            white-space: nowrap;
            text-align: right;
            direction: rtl;
            z-index: 100;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            pointer-events: none;
        }}

        .tooltip::after {{
            content: '';
            position: absolute;
            top: 100%;
            right: 50%;
            transform: translateX(50%);
            border: 5px solid transparent;
            border-top-color: #1e293b;
        }}

        /* ── רספונסיביות ── */
        @media (max-width: 600px) {{
            .card {{ width: 110px; }}
            .tag {{ font-size: 9px; }}
            .date {{ font-size: 11px; }}
            .side {{ padding: 4px 6px; }}
        }}
    </style>
</head>
<body>
    <div class="controls">
        <div class="toggle-group">
            <button class="toggle-btn active" onclick="filterView('all', this)">הכל</button>
            <button class="toggle-btn" onclick="filterView('quarter', this)">רבעון נוכחי</button>
            <button class="toggle-btn" onclick="filterView('month', this)">חודש נוכחי</button>
        </div>
    </div>

    <div class="timeline-container" id="timeline">
        {items_html}
    </div>

    <script>
        const today = new Date();
        const todayISO = today.toISOString().split('T')[0];
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        const currentQuarter = Math.floor(currentMonth / 3);

        // הוספת חיווי היום במיקום הנכון
        function insertTodayMarker() {{
            const rows = document.querySelectorAll('.timeline-row');
            const timeline = document.getElementById('timeline');
            let inserted = false;

            for (let i = 0; i < rows.length; i++) {{
                const dateStr = rows[i].getAttribute('data-date');
                if (dateStr && dateStr > todayISO) {{
                    const marker = document.createElement('div');
                    marker.className = 'today-marker';
                    marker.id = 'today-marker';
                    marker.innerHTML = '<span class="today-badge">היום {today_str}</span>';
                    timeline.insertBefore(marker, rows[i]);
                    inserted = true;
                    break;
                }}
            }}

            if (!inserted) {{
                const marker = document.createElement('div');
                marker.className = 'today-marker';
                marker.id = 'today-marker';
                marker.innerHTML = '<span class="today-badge">היום {today_str}</span>';
                timeline.appendChild(marker);
            }}
        }}

        insertTodayMarker();

        function filterView(mode, btn) {{
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const rows = document.querySelectorAll('.timeline-row');
            rows.forEach(function(row) {{
                const dateStr = row.getAttribute('data-date');
                // עבור שורות paired — בודקים את הכרטיסים הפנימיים
                const cards = row.querySelectorAll('.card');
                let anyVisible = false;

                cards.forEach(function(card) {{
                    const cDate = card.getAttribute('data-date');
                    if (!cDate) {{ anyVisible = true; return; }}
                    const date = new Date(cDate);
                    const month = date.getMonth();
                    const year = date.getFullYear();
                    const quarter = Math.floor(month / 3);

                    let show = true;
                    if (mode === 'month') {{
                        show = month === currentMonth && year === currentYear;
                    }} else if (mode === 'quarter') {{
                        show = quarter === currentQuarter && year === currentYear;
                    }}

                    card.style.visibility = show ? 'visible' : 'hidden';
                    if (show) anyVisible = true;
                }});

                // מסתיר את השורה כולה אם אין כרטיסים גלויים
                row.classList.toggle('hidden', !anyVisible && mode !== 'all');
                if (mode === 'all') {{
                    row.classList.remove('hidden');
                    row.querySelectorAll('.card').forEach(c => c.style.visibility = 'visible');
                }}
            }});

            // חיווי היום — תמיד גלוי
            const marker = document.getElementById('today-marker');
            if (marker) marker.style.display = 'flex';
        }}
    </script>
</body>
</html>"""

    return html


def show_workplan_page(project_name=None):
    import streamlit as st
    import streamlit.components.v1 as components
    st.markdown(f"### תוכנית עבודה — {project_name}", unsafe_allow_html=True)
    try:
        html = build_timeline_html(project_name)
        components.html(html, height=600, scrolling=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת תוכנית העבודה: {e}")
