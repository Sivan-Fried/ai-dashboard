import streamlit as st
import pandas as pd

def show_resources_page(project_name):
    try:
        df = pd.read_excel("resources.xlsx")
    except FileNotFoundError:
        st.error("קובץ המשאבים לא נמצא.")
        return

    df.columns = df.columns.str.strip()
    project_df = df[df['project_name'].str.strip() == project_name.strip()]

    if project_df.empty:
        st.info("לא נמצאו משאבים לפרויקט זה.")
        return

    active_df   = project_df[project_df['worker_status'].str.strip() == 'פעיל']
    inactive_df = project_df[project_df['worker_status'].str.strip() != 'פעיל']

    total_workers    = len(project_df)
    total_employment = project_df['%_employment'].str.replace('%','').astype(float).sum()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fdf2f8;">
                    <span class="material-symbols-rounded" style="color:#f0b8cb;">groups</span>
                </div>
                <span class="kpi-badge" style="background:#fdf2f8; color:#6f5861;">צוות</span>
            </div>
            <div class="kpi-content">
                <div class="kpi-value-row">
                    <span class="kpi-unit">חברי צוות</span>
                    <span class="kpi-number">{total_workers}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#f8fafc;">
                    <span class="material-symbols-rounded" style="color:#94a3b8;">work_history</span>
                </div>
                <span class="kpi-badge" style="background:#f8fafc; color:#64748b;">משרות</span>
            </div>
            <div class="kpi-content">
                <div class="kpi-value-row">
                    <span class="kpi-unit">סה"כ</span>
                    <span class="kpi-number">{total_employment:.0f}%</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('### <span class="material-symbols-outlined" style="vertical-align:middle; margin-left:8px; font-size:1.5rem; color:#64748b;">group</span> צוות פעיל', unsafe_allow_html=True)
        if not active_df.empty:
            for _, row in active_df.iterrows():
                st.markdown(f'''
                <div class="record-row">
                    <span style="display:flex; align-items:center; gap:8px; font-size:0.92rem;">
                        <span class="material-symbols-outlined" style="font-size:18px; color:#64748b;">person</span>
                        {row["worker_name"]} — {row["job title"]}
                    </span>
                    <span class="tag-pink">{row["%_employment"]}</span>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.write("אין חברי צוות פעילים.")

    if not inactive_df.empty:
        with st.container(border=True):
            st.markdown('### <span class="material-symbols-outlined" style="vertical-align:middle; margin-left:8px; font-size:1.5rem; color:#94a3b8;">group_off</span> חברי צוות בעבר', unsafe_allow_html=True)
            for _, row in inactive_df.iterrows():
                st.markdown(f'''
                <div class="record-row" style="opacity:0.5;">
                    <span style="display:flex; align-items:center; gap:8px; font-size:0.92rem;">
                        <span class="material-symbols-outlined" style="font-size:18px; color:#94a3b8;">person_off</span>
                        {row["worker_name"]} — {row["job title"]}
                    </span>
                    <span class="tag-gray">{row["%_employment"]}</span>
                </div>
                ''', unsafe_allow_html=True)
