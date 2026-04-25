import pandas as pd
import datetime
import re


# ---------------------------------------------------------
# ניקוי טקסט מתווים נסתרים, RTL, רווחים וכו'
# ---------------------------------------------------------
def clean_text(x):
    if not isinstance(x, str):
        x = str(x)

    x = x.strip()

    # תווי RTL נסתרים
    x = re.sub(r'[\u200f\u202b\u202c\u202d\u202e]', '', x)

    # תווים לא מודפסים
    x = re.sub(r'[\x00-\x1F\x7F]', '', x)

    return x


# ---------------------------------------------------------
# 1. טעינת קובץ ה־Excel
# ---------------------------------------------------------
def load_workplan_df():
    df = pd.read_excel("work_plans.xlsx")

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
        tag_class = "amit"

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
# 4. תבנית ה־HTML הגנרית
# ---------------------------------------------------------
def get_base_html(today_right, today_str):
    return f"""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@200;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family
