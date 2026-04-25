import pandas as pd
import datetime
import re


# ---------------------------------------------------------
# פונקציה שמנקה טקסט מתווים נסתרים, רווחים, RTL וכו'
# ---------------------------------------------------------
def clean_text(x):
    if not isinstance(x, str):
        x = str(x)

    # הסרת רווחים
    x = x.strip()

    # הסרת תווי RTL נסתרים
    x = re.sub(r'[\u200f\u202b\u202c\u202d\u202e]', '', x)

    # הסרת תווים לא מודפסים
    x = re.sub(r'[\x00-\x1F\x7F]', '', x)

    return x


# ---------------------------------------------------------
# 1. טעינת קובץ ה־Excel
# ---------------------------------------------------------
def load_workplan_df():
    df = pd.read_excel("work_plans.xlsx")

    # המרת תאריכים
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")

    # ניקוי שמות פרויקטים
    df["project_name"] = df["project_name"].apply(clean_text)

    return df


# ---------------------------------------------------------
# 2. יצירת HTML עבור milestone בודד
# ---------------------------------------------------------
def milestone_to_html(row):

    name = str(row["milestone_name"])

    # מיפוי לפי מילת מפתח
    if "עמיתים" in name:
        tag_class = "amit"
    elif "מעסיקים" in name:
        tag_class = "measy"
    elif "סוכנים" in name:
        tag_class = "soch"
    else:
        tag_class = "amit"  # ברירת מחדל

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
