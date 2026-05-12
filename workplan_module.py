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
    x = re.sub(r'[\u200f\u202b\u202c\u202d\u202e]', '', x)
    x = re.sub(r'[\x00-\x1F\x7F]', '', x)
    return x


# ---------------------------------------------------------
# 1. טעינת קובץ ה־Excel
# ---------------------------------------------------------
def load_workplan_df():
    df = pd.read_excel("work_plans.xlsx")
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")
    df["project_name"] = df["project_name"].apply(clean_text)
    return df


# ---------------------------------------------------------
# 2. יצירת HTML עבור milestone בודד
# ---------------------------------------------------------
def milestone_to_html(row):
    name = str(row["milestone_name"])
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

    date_str = row["date"].strftime("%d.%m.%Y")
    date_iso = row["date"].strftime("%Y-%m-%d")

    contents = str(row.get("version_contents", "")).strip()
    contents_html = contents.replace("\n", "<br>") if contents and contents != "nan" else ""
    tooltip_html = f"<div class='tooltip'>{contents_html}</div>" if contents_html else ""

    return (
        "<div class='item' data-date='" + date_iso + "'>"
        "<div class='card'>"
        + tooltip_html +
        "<span class='tag " + tag_class + "'>" + str(row['milestone_name']) + "</span>"
        "<div class='date'>" + date_str + "</div>"
        "<span class='status " + status_class + "'>" + str(row['status']) + "</span>"
        "</div>"
        "<div class='connector'></div>"
        "<div class='dot'></div>"
        "</div>"
    )


# ---------------------------------------------------------
# 3. בניית HTML של כל ה־items מתוך ה־Excel
# ---------------------------------------------------------
def build_items_html(project_df):
    return "\n".join(project_df.apply(milestone_to_html, axis=1))


# ---------------------------------------------------------
# 4. תבנית HTML ללא f-string
# ---------------------------------------------------------
BASE_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@200;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Assistant', sans-serif; background-color: white; margin: 0; padding: 0; overflow: hidden; height: 320px; }
        .controls { display: flex; justify-content: flex-end; padding: 16px 50px 0 50px; }
        .toggle-group { display: flex; background: white; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 4px; }
        .toggle-btn { padding: 6px 16px; font-size: 13px; font-weight: 600; font-family: 'Assistant', sans-serif; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; color: #94a3b8; background: transparent; }
        .toggle-btn.active { background: #FADCE6; color: #63646c; }
        .toggle-btn:hover:not(.active) { color: #475569; }
        .timeline-scroll { overflow-x: auto; overflow-y: hidden; padding: 0 50px; scrollbar-width: thin; scrollbar-color: #e2e8f0 transparent; }
        .timeline-scroll::-webkit-scrollbar { height: 4px; }
        .timeline-scroll::-webkit-scrollbar-track { background: transparent; }
        .timeline-scroll::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 2px; }
        .timeline-wrapper { position: relative; margin: 30px 0; height: 200px; display: flex; justify-content: space-between; align-items: flex-end; min-width: 1000px; }
        .main-line { position: absolute; bottom: 6px; left: 0; right: 0; height: 1px; background: #cbd5e1; z-index: 1; }
        .today-indicator { position: absolute; bottom: -10px; RIGHT_PLACEHOLDER; display: flex; flex-direction: column; align-items: center; z-index: 2; }
        .today-line { width: 2px; height: 220px; border-left: 2px dashed #cbd5e1; }
        .today-text { color: #94a3b8; font-size: 11px; font-weight: 700; margin-bottom: 4px; }
        .item { display: flex; flex-direction: column; align-items: center; width: 90px; z-index: 3; position: relative; }
        .card { background: white; padding: 4px 6px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; text-align: center; width: 100%; margin-bottom: 8px; position: relative; }
        .connector { width: 1px; height: 15px; background: #e2e8f0; }
        .dot { width: 12px; height: 12px; background: #475569; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 1px #475569; z-index: 4; }
        .tag { font-size: 11px; font-weight: 700; padding: 1px 4px; border-radius: 2px; display: inline-block; margin-bottom: 2px; }
        .amit  { background: #FADCE6; color: #831843; }
        .measy { background: #eff6ff; color: #1e40af; }
        .soch  { background: #fff7ed; color: #9a3412; }
        .date { font-size: 13px; font-weight: 600; color: #1e293b; margin: 0; }
        .status { font-size: 10px; font-weight: 700; margin-top: 2px; }
        .live { color: #10b981; }
        .wip { color: #f59e0b; }
        .tooltip { display: none; position: absolute; bottom: 110%; right: 50%; transform: translateX(50%); background: #1e293b; color: white; font-size: 11px; line-height: 1.6; padding: 8px 12px; border-radius: 8px; white-space: nowrap; text-align: right; direction: rtl; z-index: 100; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .tooltip::after { content: ''; position: absolute; top: 100%; right: 50%; transform: translateX(50%); border: 5px solid transparent; border-top-color: #1e293b; }
        .card:hover .tooltip { display: block; }
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
    <div class="timeline-scroll">
        <div class="timeline-wrapper">
            <div class="main-line"></div>
            <div class="today-indicator">
                <span class="today-text">TODAY_PLACEHOLDER</span>
                <div class="today-line"></div>
            </div>
            ITEMS_PLACEHOLDER
        </div>
    </div>
    <script>
        const today = new Date();
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        const currentQuarter = Math.floor(currentMonth / 3);
        function filterView(mode, btn) {
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.item').forEach(item => {
                const dateStr = item.dataset.date;
                if (!dateStr) { item.style.display = ''; return; }
                const date = new Date(dateStr);
                const month = date.getMonth();
                const year = date.getFullYear();
                const quarter = Math.floor(month / 3);
                let show = true;
                if (mode === 'month') { show = month === currentMonth && year === currentYear; }
                else if (mode === 'quarter') { show = quarter === currentQuarter && year === currentYear; }
                item.style.display = show ? '' : 'none';
            });
        }

        // מיקום today indicator לפי DOM
        window.addEventListener('load', function() {
            var today = new Date();
            today.setHours(0,0,0,0);

            var items = document.querySelectorAll('.item[data-date]');
            var wrapper = document.querySelector('.timeline-wrapper');
            var todayEl = document.querySelector('.today-indicator');

            if (!wrapper || !todayEl || items.length === 0) return;

            var wrapperRect = wrapper.getBoundingClientRect();

            // מצא את הפריט שתאריכו הכי קרוב לפני today
            var bestItem = null;
            var bestDate = null;

            items.forEach(function(item) {
                var itemDate = new Date(item.dataset.date);
                itemDate.setHours(0,0,0,0);
                if (itemDate <= today) {
                    if (!bestDate || itemDate > bestDate) {
                        bestDate = itemDate;
                        bestItem = item;
                    }
                }
            });

            if (bestItem) {
                var itemRect = bestItem.getBoundingClientRect();
                var todayRight = wrapperRect.right - itemRect.left - itemRect.width - 30;
                todayEl.style.right = Math.max(10, todayRight) + 'px';
            } else {
                // כל הפריטים אחרי today
                var firstRect = items[0].getBoundingClientRect();
                todayEl.style.right = (wrapperRect.right - firstRect.right + firstRect.width + 20) + 'px';
            }
        });
    </script>
</body>
</html>
"""


# ---------------------------------------------------------
# 5. בניית HTML מלא
# ---------------------------------------------------------
def build_timeline_html(project_name):
    df = load_workplan_df()
    project_name = clean_text(project_name)
    project_df = df[df["project_name"] == project_name].copy()
    project_df = project_df.sort_values("date")

    if project_df.empty:
        return "<div style='text-align:right; font-size:16px; padding:10px;'>אין נתונים עבור הפרויקט</div>"

    today = datetime.date.today()
    today_str = today.strftime("%d.%m")

    timeline_start = datetime.date(today.year, 3, 8)
    timeline_end   = datetime.date(today.year, 10, 1)
    total_days     = (timeline_end - timeline_start).days
    timeline_width = 900

    days_passed = (today - timeline_start).days
    days_passed = max(0, min(days_passed, total_days))
    today_right = int(timeline_width - (days_passed / total_days * timeline_width)) + 50

    items_html = build_items_html(project_df)

    html = BASE_HTML
    html = html.replace("RIGHT_PLACEHOLDER", f"right: {today_right}px;")
    html = html.replace("TODAY_PLACEHOLDER", f"היום {today_str}")
    html = html.replace("ITEMS_PLACEHOLDER", items_html)

    return html


def show_workplan_page(project_name=None):
    import streamlit as st
    import streamlit.components.v1 as components
    st.markdown(f"### תוכנית עבודה — {project_name}", unsafe_allow_html=True)
    try:
        html = build_timeline_html(project_name)
        components.html(html, height=320, scrolling=False)
    except Exception as e:
        st.error(f"שגיאה בטעינת תוכנית העבודה: {e}")
