import streamlit as st
import urllib.parse
import pandas as pd
import datetime

# דמה של נתונים כדי לבדוק את הממשק בלי לגעת בקוד המקורי
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

# מבנה עמודות כמו בקוד שלך
col_right, col_left = st.columns([1, 1])

# ══════════════════════════════════════════════════════
# עמודה ימנית לבדיקה
# ══════════════════════════════════════════════════════
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

    # --- עוזר אישי AI ---  (בלוק עצמאי, מחוץ לבלוק המשימות)
    with st.container(border=True):

        html_ai = """
        <div class="ai-card">

            <div class="ai-header">
                <span class="material-symbols-outlined ai-icon">smart_toy</span>
                <h4>עוזר ה‑AI שלך</h4>
            </div>

            <p class="ai-description">
                שאלי אותי כל דבר על הפרויקטים שלך או צרי משימה חדשה.
            </p>
        """
        st.markdown(html_ai, unsafe_allow_html=True)

        # בחירת פרויקט
        sel_p = st.selectbox(
            "",
            ["כללי - כל הפרויקטים"] + projects["project_name"].tolist(),
            key="ai_p_test"
        )

        # שדה שאלה
        q_in = st.text_area(
            "",
            placeholder="איך אוכל לעזור?",
            key="ai_i_test",
            height=130
        )

        # כפתור שליחה (בתוך הכרטיס)
        st.markdown("""
            <div class="ai-send-btn">
                <span class="material-symbols-outlined">arrow_back</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # כאן אין קריאה חיצונית ל‑API — רק סימולציה של תגובה
        if st.button("שגר שאילתה 🚀", use_container_width=True):
            if q_in:
                with st.spinner("מנתח..."):
                    # סימולציה של תשובת AI — רק כדי לבדוק UI ולוגיקה
                    reply = f"נבדק: פרויקט = {sel_p} | שאלה = {q_in}"
                    st.session_state.ai_response_test = reply

    # הצגת תשובה
    if st.session_state.get("ai_response_test"):
        st.info(st.session_state["ai_response_test"])

    # ── פרויקטים לדיווח ─────────────────────────────────
    with st.container(border=True):
        st.markdown("### 📌 פרויקטים לדיווח")
        for _, row in priority_df.iterrows():
            st.markdown(f"- {row['project_name']} ({row['project_number']} | {row['order_number']})", unsafe_allow_html=True)

# עמודה שמאלית מינימלית כדי לא לשבור את הפריסה
with col_left:
    with st.container(border=True):
        st.markdown("### 📅 פגישות היום")
        st.write("אין פגישות היום")
