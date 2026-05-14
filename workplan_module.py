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
    today_iso = today.strftime("%Y-%m-%d")

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

    def make_card(it, side):
        return f"""<div class="card-wrap {side}">
                    <div class="connector"></div>
                    <div class="card" data-date="{it['date_iso']}">
                        {it['tooltip_html']}
                        <span class="tag {it['tag_class']}">{it['name']}</span>
                        <div class="date">{it['date_str']}</div>
                        <span class="status {it['status_class']}">{it['status_val']}</span>
                    </div>
                </div>"""

    # בניית שורות
    items_html_parts = []
    i = 0
    side_counter = 0

    while i < len(items_data):
        item = items_data[i]
        same_date_group = [item]
        j = i + 1
        while j < len(items_data) and items_data[j]["date_iso"] == item["date_iso"]:
            same_date_group.append(items_data[j])
            j += 1

        if len(same_date_group) >= 2:
            left_card = make_card(same_date_group[0], "left")
            right_card = make_card(same_date_group[1], "right")
            items_html_parts.append(f"""
        <div class="timeline-row paired" data-date="{item['date_iso']}">
            <div class="side left">{left_card}</div>
            <div class="center-col"><div class="dot"></div></div>
            <div class="side right">{right_card}</div>
        </div>""")
            side_counter += 2
        else:
            side = "left" if side_counter % 2 == 0 else "right"
            card = make_card(item, side)
            if side == "left":
                items_html_parts.append(f"""
        <div class="timeline-row single" data-date="{item['date_iso']}">
            <div class="side left">{card}</div>
            <div class="center-col"><div class="dot"></div></div>
            <div class="side right"></div>
        </div>""")
            else:
                items_html_parts.append(f"""
        <div class="timeline-row single" data-date="{item['date_iso']}">
            <div class="side left"></div>
            <div class="center-col"><div class="dot"></div></div>
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
        }}

        .controls {{
            display: flex;
            justify-content: flex-end;
            padding: 14px 20px 8px 20px;
        }}

        .toggle-group {{
            display: flex;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            padding: 4px;
        }}

        .toggle-btn {{
            padding: 5px 12px;
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

        /* ציר הזמן */
        .timeline-container {{
            position: relative;
            padding: 16px 0 32px 0;
        }}

        /* קו ציר אנכי */
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

        /* חיווי היום */
        .today-marker {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 28px;
            margin: 6px 0;
            z-index: 5;
        }}

        .today-marker::before {{
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            border-top: 2px dashed #f0b8cb;
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

        /* שורת ציר */
        .timeline-row {{
            display: grid;
            grid-template-columns: 1fr 40px 1fr;
            align-items: center;
            min-height: 90px;
            position: relative;
            z-index: 2;
        }}

        .timeline-row.hidden {{
            display: none !important;
        }}

        /* עמודת מרכז */
        .center-col {{
            display: flex;
            justify-content: center;
            align-items: center;
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
            z-index: 4;
        }}

        /* צדדים */
        .side {{
            display: flex;
            align-items: center;
            padding: 8px 0;
        }}

        .side.left {{
            justify-content: flex-end;
        }}

        .side.right {{
            justify-content: flex-start;
        }}

        /* עטיפת כרטיס */
        .card-wrap {{
            display: flex;
            align-items: center;
        }}

        /* כרטיס שמאל: קונקטור אחרי הכרטיס (בצד ימין של הכרטיס = כיוון המרכז) */
        .card-wrap.left {{
            flex-direction: row-reverse;
        }}

        /* כרטיס ימין: קונקטור לפני הכרטיס (בצד שמאל של הכרטיס = כיוון המרכז) */
        .card-wrap.right {{
            flex-direction: row;
        }}

        .connector {{
            height: 2px;
            width: 16px;
            background: #cbd5e1;
            flex-shrink: 0;
        }}

        /* כרטיס */
        .card {{
            background: white;
            padding: 6px 8px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.07);
            border: 1px solid #f1f5f9;
            text-align: center;
            width: 120px;
            position: relative;
            flex-shrink: 0;
        }}

        .card:hover .tooltip {{ display: block; }}

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
            margin: 2px 0;
        }}

        .status {{
            font-size: 9px;
            font-weight: 700;
            margin-top: 1px;
            display: block;
            color: #94a3b8;
        }}
        .live {{ color: #10b981; }}
        .wip  {{ color: #f59e0b; }}

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

        @media (max-width: 500px) {{
            .card {{ width: 90px; }}
            .tag {{ font-size: 9px; }}
            .date {{ font-size: 10px; }}
            .connector {{ width: 8px; }}
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
        var todayISO = '{today_iso}';
        var currentMonth = new Date().getMonth();
        var currentYear = new Date().getFullYear();
        var currentQuarter = Math.floor(currentMonth / 3);

        function insertTodayMarker() {{
            var rows = document.querySelectorAll('.timeline-row');
            var timeline = document.getElementById('timeline');
            var marker = document.createElement('div');
            marker.className = 'today-marker';
            marker.id = 'today-marker';
            marker.innerHTML = '<span class="today-badge">היום {today_str}</span>';

            var inserted = false;
            for (var i = 0; i < rows.length; i++) {{
                var d = rows[i].getAttribute('data-date');
                if (d && d > todayISO) {{
                    timeline.insertBefore(marker, rows[i]);
                    inserted = true;
                    break;
                }}
            }}
            if (!inserted) timeline.appendChild(marker);
        }}

        insertTodayMarker();

        function filterView(mode, btn) {{
            document.querySelectorAll('.toggle-btn').forEach(function(b) {{
                b.classList.remove('active');
            }});
            btn.classList.add('active');

            var rows = document.querySelectorAll('.timeline-row');
            rows.forEach(function(row) {{
                if (mode === 'all') {{
                    row.classList.remove('hidden');
                    row.querySelectorAll('.card-wrap').forEach(function(w) {{
                        w.style.visibility = 'visible';
                    }});
                    return;
                }}

                var cards = row.querySelectorAll('.card');
                var anyVisible = false;

                cards.forEach(function(card) {{
                    var cDate = card.getAttribute('data-date');
                    if (!cDate) {{ anyVisible = true; return; }}
                    var date = new Date(cDate);
                    var month = date.getMonth();
                    var year = date.getFullYear();
                    var quarter = Math.floor(month / 3);
                    var show = true;
                    if (mode === 'month') {{
                        show = (month === currentMonth && year === currentYear);
                    }} else if (mode === 'quarter') {{
                        show = (quarter === currentQuarter && year === currentYear);
                    }}
                    var wrap = card.closest('.card-wrap');
                    if (wrap) wrap.style.visibility = show ? 'visible' : 'hidden';
                    if (show) anyVisible = true;
                }});

                if (anyVisible) {{
                    row.classList.remove('hidden');
                }} else {{
                    row.classList.add('hidden');
                }}
            }});

            var marker = document.getElementById('today-marker');
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
        components.html(html, height=700, scrolling=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת תוכנית העבודה: {e}")
