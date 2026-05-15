import streamlit as st
import pandas as pd

def show_resources_page(project_name):
    try:
        df = pd.read_excel("resources.xlsx")
    except FileNotFoundError:
        st.error("קובץ המשאבים לא נמצא.")
        return

    df.columns = df.columns.str.strip()
    project_df = df[df['project_name'].str.strip() == project_name.strip()].copy()

    if project_df.empty:
        st.info("לא נמצאו משאבים לפרויקט זה.")
        return

    # נתוני הפרויקט מ-my_projects.xlsx
    onboarding_days = 60
    skills_list = []
    try:
        projects_df = pd.read_excel("my_projects.xlsx")
        proj_row = projects_df[projects_df['project_name'].str.strip() == project_name.strip()]
        if not proj_row.empty:
            onboarding_days = int(proj_row.iloc[0].get('onboarding', 60))
            skills_raw = str(proj_row.iloc[0].get('skills', ''))
            if skills_raw and skills_raw != 'nan':
                skills_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
    except:
        pass

    active_df   = project_df[project_df['worker_status'].str.strip() == 'פעיל']
    inactive_df = project_df[project_df['worker_status'].str.strip() != 'פעיל']

    total_workers = len(active_df)
    emp_numeric = pd.to_numeric(project_df['%_employment'].astype(str).str.replace('%',''), errors='coerce')
    if emp_numeric.max() <= 1:
        total_employment = emp_numeric.sum()
    else:
        total_employment = emp_numeric.sum() / 100

    def get_pct(val):
        v = pd.to_numeric(str(val).replace('%',''), errors='coerce')
        if pd.isna(v): return 0
        if v <= 1: return v * 100
        return v

    col1, col2, col3 = st.columns(3)
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
                    <span class="kpi-unit">חברי צוות פעילים</span>
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
                    <span class="kpi-unit">משרות אדם</span>
                    <span class="kpi-number">{total_employment:.1f}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#f0fdf4;">
                    <span class="material-symbols-rounded" style="color:#86efac;">schedule</span>
                </div>
                <span class="kpi-badge" style="background:#f0fdf4; color:#16a34a;">Onboarding</span>
            </div>
            <div class="kpi-content">
                <div class="kpi-value-row">
                    <span class="kpi-unit">ימים</span>
                    <span class="kpi-number">{onboarding_days}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    def render_table(rows_df, title):
        st.markdown(f'### {title}', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('''
            <div style="display:grid; grid-template-columns: 2fr 2fr 1.5fr 2fr; gap:8px; padding:8px 16px; 
                        border-bottom:1px solid #f1f5f9; direction:rtl; margin-bottom:4px; text-align:right;">
                <span style="font-size:0.78rem; font-weight:700; color:#94a3b8;">שם העובד</span>
                <span style="font-size:0.78rem; font-weight:700; color:#94a3b8;">תפקיד</span>
                <span style="font-size:0.78rem; font-weight:700; color:#94a3b8;">אחוזי משרה</span>
                <span style="font-size:0.78rem; font-weight:700; color:#94a3b8;">הערות</span>
            </div>
            ''', unsafe_allow_html=True)
            
            for _, row in rows_df.iterrows():
                pct = get_pct(row["%_employment"])
                st.markdown(f'''
                <div style="display:grid; grid-template-columns: 2fr 2fr 1.5fr 2fr; gap:8px; 
                            padding:12px 16px; border-bottom:1px solid #f9f9f9; 
                            direction:rtl; align-items:center; text-align:right;">
                    <span style="font-size:0.9rem; font-weight:600; color:#3f3f46;">{row["worker_name"]}</span>
                    <span style="font-size:0.85rem; color:#71717A;">{row["job title"]}</span>
                    <div style="text-align:right;">
                        <span style="font-size:0.9rem; font-weight:700; color:#3f3f46;">{pct:.0f}%</span>
                        <div style="height:4px; background:#f1f5f9; border-radius:999px; margin-top:6px; max-width:80px;">
                            <div style="height:4px; width:{pct}%; background:#f0b8cb; border-radius:999px;"></div>
                        </div>
                    </div>
                    <span style="font-size:0.78rem; color:#94a3b8;">{row.get("notes", "")}</span>
                </div>
                ''', unsafe_allow_html=True)

    render_table(active_df, "צוות פעיל")
    
    if not inactive_df.empty:
        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)
        render_table(inactive_df, "חברי צוות בעבר")

    # Skills
    if skills_list:
        st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### כישורים נדרשים", unsafe_allow_html=True)
        
        pills_html = ""
        for skill in skills_list:
            pills_html += f"<span style='display:inline-flex;align-items:center;background:#ffffff;border:1.5px solid #FADCE6;border-radius:999px;padding:6px 16px;font-size:0.82rem;font-weight:600;color:#71717A;margin:4px;white-space:nowrap;'>{skill}</span>"
        
        st.markdown(f"<div style='display:flex;flex-wrap:wrap;direction:rtl;margin-top:8px;'>{pills_html}</div>", unsafe_allow_html=True)
