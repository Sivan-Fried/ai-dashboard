import streamlit as st
import streamlit.components.v1 as components
import datetime

# כותרת עליונה
st.markdown("<h2 style='text-align: right; color: #334155; font-family: Assistant, sans-serif; font-weight: 300; padding-right: 50px;'>תוכנית עבודה: <span style='font-weight:700'>אזורים אישיים</span></h2>", unsafe_allow_html=True)

# =========================================================
# חישוב מיקומים דינמיים לפי תאריך
# =========================================================
today = datetime.date.today()
today_str = today.strftime("%d.%m")

timeline_start = datetime.date(today.year, 3, 8)
timeline_end   = datetime.date(today.year, 10, 1)
total_days     = (timeline_end - timeline_start).days
timeline_width = 900  # px בין padding ל-padding

def date_to_right(d):
    """המרת תאריך לערך right בפיקסלים (RTL: ימין = התחלה)"""
    days = (d - timeline_start).days
    days = max(0, min(days, total_days))
    ratio = days / total_days
    # RTL: right=950 = תחילת הציר, right=50 = סופו
    return int(950 - ratio * timeline_width)

# מיקום חיווי היום
today_right = date_to_right(today)

# מיקומי הפריטים
items = [
    {"date": datetime.date(today.year, 3, 8),  "label": "08.03", "tag": "עמיתים",  "cls": "amit", "status": "LIVE", "scls": "live"},
    {"date": datetime.date(today.year, 3, 8),  "label": "08.03", "tag": "מעסיקים", "cls": "measy","status": "LIVE", "scls": "live"},
    {"date": datetime.date(today.year, 3, 24), "label": "24.03", "tag": "סוכנים",  "cls": "soch", "status": "LIVE", "scls": "live"},
    {"date": datetime.date(today.year, 4, 10), "label": "10.04", "tag": "עמיתים",  "cls": "amit", "status": "LIVE", "scls": "live"},
    {"date": datetime.date(today.year, 7, 1),  "label": "07/26", "tag": "עמיתים",  "cls": "amit", "status": "WIP",  "scls": "wip"},
    {"date": datetime.date(today.year, 10, 1), "label": "TBD",   "tag": "מעסיקים", "cls": "measy","status": "HOLD", "scls": "hold"},
]

# בניית HTML לפריטים
items_html = ""
for item in items:
    r = date_to_right(item["date"])
    hold_style = 'style="color:#94a3b8"' if item["scls"] == "hold" else ""
    items_html += f"""
        <div class="item" style="right: {r}px;">
            <div class="card">
                <span class="tag {item['cls']}">{item['tag']}</span>
                <div class="date">{item['label']}</div>
                <span class="status {item['scls']}" {hold_style}>{item['status']}</span>
            </div>
            <div class="connector"></div>
            <div class="dot"></div>
        </div>
    """

roadmap_html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@200;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Assistant', sans-serif; background-color: white; margin: 0; padding: 0; overflow: hidden; }}
        
        .timeline-wrapper {{
            position: relative;
            width: 1000px;
            margin: 50px auto;
            height: 200px;
            padding: 0 50px;
        }}

        .main-line {{
            position: absolute;
            bottom: 21px;
            left: 0;
            right: 0;
            height: 1px;
            background: #cbd5e1;
            z-index: 1;
        }}

        .today-indicator {{
            position: absolute;
            bottom: 0px;
            right: {today_right}px;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 5;
            transform: translateX(50%);
        }}
        .today-line {{
            width: 2px;
            height: 75px;
            border-left: 2px dashed #bfdbfe;
        }}
        .today-text {{
            color: #3b82f6;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 4px;
            white-space: nowrap;
        }}

        .item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100px;
            z-index: 3;
            position: absolute;
            bottom: 15px;
            transform: translateX(50%);
        }}

        .card {{
            background: white;
            padding: 6px 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
            border: 1px solid #e2e8f0;
            text-align: center;
            width: 100%;
            margin-bottom: 8px;
        }}

        .connector {{
            width: 1px;
            height: 15px;
            background: #e2e8f0;
        }}

        .dot {{
            width: 12px;
            height: 12px;
            background: #475569;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 0 1px #475569;
            z-index: 4;
        }}

        .tag    {{ font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 3px; display: inline-block; margin-bottom: 3px; }}
        .amit   {{ background: #eff6ff; color: #1e40af; }}
        .measy  {{ background: #f5f3ff; color: #5b21b6; }}
        .soch   {{ background: #ecfdf5; color: #065f46; }}
        .date   {{ font-size: 14px; font-weight: 700; color: #1e293b; margin: 0; }}
        .status {{ font-size: 9px; font-weight: 700; margin-top: 3px; display: block; }}
        .live   {{ color: #10b981; }}
        .wip    {{ color: #f59e0b; }}
    </style>
</head>
<body>
    <div class="timeline-wrapper">
        <div class="main-line"></div>
        
        <div class="today-indicator">
            <span class="today-text">היום {today_str}</span>
            <div class="today-line"></div>
        </div>

        {items_html}
    </div>
</body>
</html>
"""

components.html(roadmap_html, height=300, scrolling=False)
