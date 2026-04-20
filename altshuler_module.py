import streamlit as st
import streamlit.components.v1 as components

# 1. הגדרות דף
st.set_page_config(layout="wide")

# 2. כותרת עליונה
st.markdown("<h2 style='text-align: right; color: #334155; font-family: Assistant, sans-serif; font-weight: 300; padding-right: 50px;'>תוכנית עבודה: <span style='font-weight:700'>אזורים אישיים</span></h2>", unsafe_allow_html=True)

# 3. HTML ועיצוב עם Flexbox למניעת תזוזות
roadmap_html = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@200;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Assistant', sans-serif; background-color: white; margin: 0; padding: 0; overflow: hidden; }
        
        .timeline-wrapper {
            position: relative;
            width: 1000px;
            margin: 50px auto;
            height: 200px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end; /* מצמיד את הכל לקו התחתון */
            padding: 0 50px;
        }

        /* ציר הזמן האופקי - עובר בדיוק במרכז העיגולים */
        .main-line {
            position: absolute;
            bottom: 6px; /* חצי מגובה העיגול */
            left: 0;
            right: 0;
            height: 1px;
            background: #cbd5e1;
            z-index: 1;
        }

        /* חיווי היום - קו קטן וממוקד */
        .today-indicator {
            position: absolute;
            bottom: -15px;
            right: 525px; /* ממוקם בין 10.04 ליולי */
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 5;
        }
        .today-line {
            width: 2px;
            height: 60px;
            border-left: 2px dashed #bfdbfe;
        }
        .today-text {
            color: #3b82f6;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        /* יחידת משימה */
        .item {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 90px;
            z-index: 3;
            position: relative;
        }

        /* מלבן המשימה */
        .card {
            background: white;
            padding: 4px 6px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            border: 1px solid #f1f5f9;
            text-align: center;
            width: 100%;
            margin-bottom: 8px;
        }

        /* קו מחבר קצר */
        .connector {
            width: 1px;
            height: 15px;
            background: #e2e8f0;
        }

        /* העיגול שיושב על הקו */
        .dot {
            width: 12px;
            height: 12px;
            background: #475569;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 0 1px #475569;
            z-index: 4;
        }

        /* טקסטים */
        .tag { font-size: 8px; font-weight: 700; padding: 1px 4px; border-radius: 2px; display: inline-block; margin-bottom: 2px; }
        .amit { background: #eff6ff; color: #1e40af; }
        .measy { background: #f5f3ff; color: #5b21b6; }
        .soch { background: #ecfdf5; color: #065f46; }
        .date { font-size: 13px; font-weight: 600; color: #1e293b; margin: 0; }
        .status { font-size: 8px; font-weight: 700; margin-top: 2px; }
        .live { color: #10b981; } .wip { color: #f59e0b; }
    </style>
</head>
<body>
    <div class="timeline-wrapper">
        <div class="main-line"></div>
        
        <div class="today-indicator">
            <span class="today-text">היום 20.04</span>
            <div class="today-line"></div>
        </div>

        <div class="item">
            <div class="card"><span class="tag amit">עמיתים</span><div class="date">08.03</div><span class="status live">LIVE</span></div>
            <div class="connector"></div><div class="dot"></div>
        </div>
        
        <div class="item">
            <div class="card"><span class="tag measy">מעסיקים</span><div class="date">08.03</div><span class="status live">LIVE</span></div>
            <div class="connector"></div><div class="dot"></div>
        </div>

        <div class="item">
            <div class="card"><span class="tag soch">סוכנים</span><div class="date">24.03</div><span class="status live">LIVE</span></div>
            <div class="connector"></div><div class="dot"></div>
        </div>

        <div class="item">
            <div class="card"><span class="tag amit">עמיתים</span><div class="date">10.04</div><span class="status live">LIVE</span></div>
            <div class="connector"></div><div class="dot"></div>
        </div>

        <div class="item">
            <div class="card"><span class="tag amit">עמיתים</span><div class="date">יולי</div><span class="status wip">WIP</span></div>
            <div class="connector"></div><div class="dot"></div>
        </div>

        <div class="item">
            <div class="card"><span class="tag measy">מעסיקים</span><div class="date">TBD</div><span class="status" style="color:#94a3b8">HOLD</span></div>
            <div class="connector"></div><div class="dot"></div>
        </div>
    </div>
</body>
</html>
"""

components.html(roadmap_html, height=300, scrolling=False)