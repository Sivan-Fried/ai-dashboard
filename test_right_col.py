import streamlit as st
import urllib.parse
import pandas as pd
import datetime

# דמה של נתונים
projects = pd.DataFrame([
    {"project_name": "AnalystCustomers", "project_type": "אנליזה", "status": "ירוק"},
    {"project_name": "IDI App", "project_type": "פיתוח", "status": "צהוב"},
])
priority_df = pd.DataFrame([
    {"project_name": "אנליסט פרויקט A", "project_number": "P-001", "order_number": "O-11"},
    {"project_name": "דנאל פרויקט B", "project_number": "P-002", "order_number": "O-22"},
])
meetings = pd.DataFrame([])
today = datetime.date.today()

st.set_page_config(layout="wide")

# ⭐ CSS מלא לכרטיס הוורוד ⭐
st.markdown("""
<style>
.ai-card {
    background-color: #FADCE6;
    padding: 24px;
    border-radius: 24px;
    box-shadow: 0px 10px 30px rgba(225,200,210,0.25);
    direction: rtl;
    margin-bottom: 20px;
    width: 100%;
}

.ai-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.ai-header h4 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #6f5861;
}

.ai-description {
    font-size: 14px;
    color: #6f5861;
    opacity: 0.85;
    margin-bottom: 20px;
    text-align: right;
}

.ai-send-btn {
    position: absolute;
    left: 12px;
    bottom: 12px;
    width: 42px;
    height: 42px;
    background-color: #6f5861;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    cursor: pointer;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}

textarea {
    width: 100%;
    background: white;
    border: none;
    border-radius: 18px;
    padding: 14px;
    height: 120px;
    font-size: 14px;
    resize: none;
    outline: none;
}

select {
    width: 100%;
    background: rgba(255,255,255,0.6);
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-size: 14px;
    text-align: right;
    outline: none;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# עמודות
# ───────────────────────────────────────────────
col_right, col_left = st.columns([1, 1])

# ───────────────────────────────────────────────
# עמודה ימנית
# ───────────────────────────────────────────────
with col_right:

    # --- פרויקטים ---
    with st.container(border=True):
        st.markdown("### 📁 פרויקטים")
        with st.container(height=300, border=False):
            for _, row in projects.iterrows():
                p_url = f"/?proj={urllib.parse.quote(row['project_name'])}"
                st.markdown(f'''
                    <a href="{p_url}" target="_self" class="project-link">
                        <div class="record-row">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <b>📂 {row["project_name"]}</b>
                                <span class="tag-blue">{row.get("project_type", "תחזוקה")}</span>
                            </div>
                            <span style="color: #94a3b8; font-size: 22px; line-height: 1; flex-shrink: 0;">&#8250;</span>
                        </div>
                    </a>
                ''', unsafe_allow_html=True)

    # --- משימות ---
    with st.container(border=True):
        st.markdown('<h3>📋 משימות חדשות באז\'ור</h3>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: right; color: gray;">אין משימות חדשות.</p>', unsafe_allow_html=True)

    # ⭐ עוזר AI — עכשיו ברוחב מלא של העמודה ⭐
    st.markdown("""
    <div class="ai-card">

        <div class="ai-header">
            <span style="font-size:26px;">🤖</span>
            <h4>עוזר ה‑AI שלך</h4>
        </div>

        <p class="ai-description">
            שאלי אותי כל דבר על הפרויקטים שלך או צרי משימה חדשה.
        </p>
    """, unsafe_allow_html=True)

    sel_p = st.select
