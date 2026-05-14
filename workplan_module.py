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

    # בניית שורות HTML
    # הגישה: כל שורה היא div רגיל עם flexbox.
    # הציר האנכי הוא ::before על מיכל האב שנמצא ב-left: 50%.
    # הנקודה מוצבת ב-position: absolute במרכז.
    # הכרטיסים בשמאל/ימין עם padding מספיק.

    rows_html = []
    i = 0
    side_counter = 0

    while i < len(items_data):
        item = items_data[i]
        same_date_group = [item]
        j = i + 1
        while j < len(items_data) and items_data[j]["date_iso"] == item["date_iso"]:
            same_date_group.append(items_data[j])
            j += 1

        def card_html(it):
            return f"""<div class="card" data-date="{it['date_iso']}">
                {it['tooltip_html']}
                <span class="tag {it['tag_class']}">{it['name']}</span>
                <div class="cdate">{it['date_str']}</div>
                <span class="status {it['status_class']}">{it['status_val']}</span>
            </div>"""

        if len(same_date_group) >= 2:
            # שניים באותו תאריך — אחד משמאל אחד מימין
            left_c = card_html(same_date_group[0])
            right_c = card_html(same_date_group[1])
            rows_html.append(f"""
<div class="trow paired" data-date="{item['date_iso']}">
    <div class="tcell left">{left_c}</div>
    <div class="tcenter">
        <div class="dot"></div>
    </div>
    <div class="tcell right">{right_c}</div>
</div>""")
            side_counter += 2
        else:
            side = "left" if side_counter % 2 == 0 else "right"
            c = card_html(item)
            if side == "left":
                rows_html.append(f"""
<div class="trow single" data-date="{item['date_iso']}">
    <div class="tcell left">{c}</div>
    <div class="tcenter">
        <div class="dot"></div>
    </div>
    <div class="tcell right"></div>
</div>""")
            else:
                rows_html.append(f"""
<div class="trow single" data-date="{item['date_iso']}">
    <div class="tcell left"></div>
    <div class="tcenter">
        <div class="dot"></div>
    </div>
    <div class="tcell right">{c}</div>
</div>""")
            side_counter += 1

        i = j

    rows_str = "\n".join(rows_html)

    # חישוב גובה: שורה = ~95px, קבועים = ~120px
    num_items = len(items_data)
    # paired rows take same space as single
    approx_rows = len(rows_html)
    body_height = 80 + (approx_rows * 100) + 80

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
    background: white;
    direction: rtl;
    min-height: {body_height}px;
}}

/* ── כפתורי סינון ── */
.controls {{
    display: flex;
    justify-content: flex-end;
    padding: 14px 20px 12px 20px;
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

/* ── מיכל ציר ── */
.timeline-wrap {{
    position: relative;
    padding: 12px 0 40px 0;
}}

/* קו ציר אנכי — מוחלט, ממוקם ב-50% */
.timeline-wrap::before {{
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    width: 2px;
    margin-left: -1px;
    background: #cbd5e1;
    z-index: 0;
}}

/* ── שורת ציר ── */
.trow {{
    display: flex;
    align-items: center;
    min-height: 90px;
    position: relative;
}}

.trow.hidden {{
    display: none !important;
}}

/* תא כרטיס — 50% רוחב מינוס מקום לנקודה */
.tcell {{
    flex: 0 0 calc(50% - 20px);
    padding: 6px 0;
}}

.tcell.left {{
    display: flex;
    justify-content: flex-end;
    padding-right: 16px;
}}

.tcell.right {{
    display: flex;
    justify-content: flex-start;
    padding-left: 16px;
}}

/* עמודת מרכז — רק הנקודה, 40px רוחב */
.tcenter {{
    flex: 0 0 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    z-index: 3;
}}

/* נקודה על הציר */
.dot {{
    width: 12px;
    height: 12px;
    background: #475569;
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: 0 0 0 2px #475569;
    flex-shrink: 0;
    position: relative;
    z-index: 4;
}}

/* ── כרטיס ── */
.card {{
    background: white;
    padding: 7px 9px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    border: 1px solid #f1f5f9;
    text-align: center;
    width: 130px;
    flex-shrink: 0;
    position: relative;
}}

/* קונקטור דרך border — אין div נוסף */
.tcell.left .card::after {{
    content: '';
    position: absolute;
    top: 50%;
    right: -16px;
    transform: translateY(-50%);
    width: 16px;
    height: 2px;
    background: #cbd5e1;
}}

.tcell.right .card::before {{
    content: '';
    position: absolute;
    top: 50%;
    left: -16px;
    transform: translateY(-50%);
    width: 16px;
    height: 2px;
    background: #cbd5e1;
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

.cdate {{
    font-size: 12px;
    font-weight: 600;
    color: #1e293b;
    margin: 2px 0;
}}

.status {{
    font-size: 9px;
    font-weight: 700;
    display: block;
    color: #94a3b8;
}}
.live {{ color: #10b981; }}
.wip  {{ color: #f59e0b; }}

/* ── טולטיפ ── */
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

/* ── חיווי היום ── */
.today-marker {{
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 30px;
    margin: 4px 0;
    z-index: 5;
}}

.today-marker::before {{
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    border-top: 2px dashed #f0b8cb;
    z-index: 1;
}}

.today-badge {{
    background: #FADCE6;
    color: #63646c;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 14px;
    border-radius: 20px;
    position: relative;
    z-index: 2;
    white-space: nowrap;
}}

@media (max-width: 480px) {{
    .card {{ width: 100px; }}
    .tag {{ font-size: 9px; }}
    .cdate {{ font-size: 10px; }}
    .tcell.left {{ padding-right: 10px; }}
    .tcell.right {{ padding-left: 10px; }}
    .tcell.left .card::after {{ right: -10px; width: 10px; }}
    .tcell.right .card::before {{ left: -10px; width: 10px; }}
}}
</style>
</head>
<body>

<div class="controls">
    <div class="toggle-group">
        <button class="toggle-btn active" onclick="filterView('all',this)">הכל</button>
        <button class="toggle-btn" onclick="filterView('quarter',this)">רבעון נוכחי</button>
        <button class="toggle-btn" onclick="filterView('month',this)">חודש נוכחי</button>
    </div>
</div>

<div class="timeline-wrap" id="timeline">
{rows_str}
</div>

<script>
var todayISO = '{today_iso}';
var currentMonth = new Date().getMonth();
var currentYear  = new Date().getFullYear();
var currentQ     = Math.floor(currentMonth / 3);

function insertTodayMarker() {{
    var rows = document.querySelectorAll('.trow');
    var tl   = document.getElementById('timeline');
    var m    = document.createElement('div');
    m.className = 'today-marker';
    m.id = 'today-marker';
    m.innerHTML = '<span class="today-badge">היום {today_str}</span>';

    var placed = false;
    for (var i = 0; i < rows.length; i++) {{
        if (rows[i].getAttribute('data-date') > todayISO) {{
            tl.insertBefore(m, rows[i]);
            placed = true;
            break;
        }}
    }}
    if (!placed) tl.appendChild(m);
}}

insertTodayMarker();

function filterView(mode, btn) {{
    document.querySelectorAll('.toggle-btn').forEach(function(b){{ b.classList.remove('active'); }});
    btn.classList.add('active');

    document.querySelectorAll('.trow').forEach(function(row) {{
        if (mode === 'all') {{
            row.classList.remove('hidden');
            row.querySelectorAll('.card').forEach(function(c){{ c.style.opacity='1'; }});
            return;
        }}
        var cards = row.querySelectorAll('.card');
        var any = false;
        cards.forEach(function(card) {{
            var d = card.getAttribute('data-date');
            if (!d) {{ any = true; return; }}
            var dt = new Date(d);
            var show = true;
            if (mode === 'month') {{
                show = dt.getMonth()===currentMonth && dt.getFullYear()===currentYear;
            }} else if (mode === 'quarter') {{
                show = Math.floor(dt.getMonth()/3)===currentQ && dt.getFullYear()===currentYear;
            }}
            card.style.opacity = show ? '1' : '0';
            if (show) any = true;
        }});
        row.classList.toggle('hidden', !any);
    }});

    var m = document.getElementById('today-marker');
    if (m) m.style.display = 'flex';
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
        df = load_workplan_df()
        p = clean_text(project_name) if project_name else ""
        project_df = df[df["project_name"] == p]
        num_rows = max(len(project_df), 1)
        dynamic_height = 120 + (num_rows * 100) + 80
        html = build_timeline_html(project_name)
        components.html(html, height=dynamic_height, scrolling=False)
    except Exception as e:
        st.error(f"שגיאה בטעינת תוכנית העבודה: {e}")
