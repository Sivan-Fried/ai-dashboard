import pandas as pd
import datetime
import pandas as pd


# ---------------------------------------------------------
# 1. טעינת קובץ ה־Excel
# ---------------------------------------------------------
def load_workplan_df():
    df = pd.read_excel("work_plans.xlsx")
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")
    return df

# ---------------------------------------------------------
# 2. יצירת HTML עבור milestone בודד
# ---------------------------------------------------------
def milestone_to_html(row):
    tag_class = {
        "עמיתים": "amit",
        "מעסיקים": "measy",
        "סוכנים": "soch"
    }.get(row["milestone_name"], "amit")

    status_class = {
        "LIVE": "live",
        "WIP": "wip",
        "HOLD": ""
    }.get(row["status"], "")

    return f"""
    <div class="item">
        <div class="card">
            <span class="tag {tag_class}">{row['milestone_name']}</span>
            <div class="date">{row['date']}</div>
            <span class="status {status_class}">{row['status']}</span>
        </div>
        <div class="connector"></div>
        <div class="dot"></div>
    </div>
    """


# ---------------------------------------------------------
# 3. בניית HTML של כל ה־items מתוך ה־Excel
# ---------------------------------------------------------
def build_items_html(project_df):
    return "\n".join(project_df.apply(milestone_to_html, axis=1))


# ---------------------------------------------------------
# 4. תבנית ה־HTML הגנרית (עם placeholder)
# ---------------------------------------------------------
def get_base_html(today_right, today_str):
    return f"""
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
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding: 0 50px;
        }}

        .main-line {{
            position: absolute;
            bottom: 6px;
            left: 0;
            right: 0;
            height: 1px;
            background: #cbd5e1;
            z-index: 1;
        }}

        .today-indicator {{
            position: absolute;
            bottom: -15px;
            right: {today_right}px;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 5;
        }}
        .today-line {{
            width: 2px;
            height: 60px;
            border-left: 2px dashed #bfdbfe;
        }}
        .today-text {{
            color: #3b82f6;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 90px;
            z-index: 3;
            position: relative;
        }}

        .card {{
            background: white;
            padding: 4px 6px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            border: 1px solid #f1f5f9;
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

        .tag {{ font-size: 8px; font-weight: 700; padding: 1px 4px; border-radius: 2px; display: inline-block; margin-bottom: 2px; }}
        .amit {{ background: #eff6ff; color: #1e40af; }}
        .measy {{ background: #f5f3ff; color: #5b21b6; }}
        .soch {{ background: #ecfdf5; color: #065f46; }}
        .date {{ font-size: 13px; font-weight: 600; color: #1e293b; margin: 0; }}
        .status {{ font-size: 8px; font-weight: 700; margin-top: 2px; }}
        .live {{ color: #10b981; }} 
        .wip {{ color: #f59e0b; }}
    </style>
</head>
<body>
    <div class="timeline-wrapper">
        <div class="main-line"></div>
        
        <div class="today-indicator">
            <span class="today-text">היום {today_str}</span>
            <div class="today-line"></div>
        </div>

        <!-- ITEMS_PLACEHOLDER -->

    </div>
</body>
</html>
"""


# ---------------------------------------------------------
# 5. פונקציה גנרית שמחזירה HTML מלא לפרויקט
# ---------------------------------------------------------
def build_timeline_html(project_name):
    df = load_workplan_df()   # ← ← ← התיקון היחיד
    project_df = df[df["project_name"] == project_name].copy()

    # חישוב תאריך היום
    today = datetime.date.today()
    today_str = today.strftime("%d.%m")

    # חישוב מיקום היום על הציר
    timeline_start = datetime.date(today.year, 3, 8)
    timeline_end   = datetime.date(today.year, 10, 1)
    total_days     = (timeline_end - timeline_start).days
    timeline_width = 900

    days_passed = (today - timeline_start).days
    days_passed = max(0, min(days_passed, total_days))
    today_right = int(timeline_width - (days_passed / total_days * timeline_width)) + 50

    # יצירת items
    items_html = build_items_html(project_df)

    # הזרקת items לתוך התבנית
    base_html = get_base_html(today_right, today_str)
    final_html = base_html.replace("<!-- ITEMS_PLACEHOLDER -->", items_html)

    return final_html
