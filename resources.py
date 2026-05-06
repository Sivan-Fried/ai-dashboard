import streamlit as st
import pandas as pd
import numpy as np

def show_resources_page():
    # ==========================================
    # אזור: כותרת העמוד
    # ==========================================
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: end; margin-bottom: 32px;">
        <div>
            <h2 style="font-size: 32px; font-weight: 600; color: #6f5861; margin-bottom: 8px;">ניהול משאבי פרויקט - Aura</h2>
            <p style="color: #4e4447; font-size: 16px;">סקירה וניהול הקצאות צוות בזמן אמת</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # טעינת הנתונים
    try:
        df = pd.read_csv("resources.xlsx - Sheet1.csv")
    except FileNotFoundError:
        st.error("קובץ המשאבים לא נמצא. ודאי שהקובץ נמצא בתיקיית הפרויקט.")
        return

    # ניקוי רווחים משמות העמודות
    df.columns = df.columns.str.strip()
    
    # סינון לפי פרויקט (דוגמה: בחירת פרויקט או הצגת הכל)
    projects = df['project_name'].unique().tolist()
    selected_project = st.selectbox("בחר פרויקט:", projects)
    
    project_df = df[df['project_name'] == selected_project]

    # ==========================================
    # אזור: סיכום נתונים (KPI/Summary)
    # ==========================================
    active_workers = project_df[project_df['worker_status'].str.strip() == 'פעיל']
    
    total_workers = len(project_df)
    
    # חישוב אחוזי משרה (טיפול בהמרה למספרים)
    total_employment = project_df['%_employment'].sum() * 100

    st.markdown("""
    <style>
    .kpi-card { 
        background: #f9f9f9; 
        padding: 24px; 
        border-radius: 12px; 
        box-shadow: 0px 10px 30px rgba(225, 200, 210, 0.15); 
        border: 1px solid rgba(127, 116, 119, 0.1); 
        display: flex; 
        align-items: center; 
        gap: 24px; 
    }
    .kpi-icon {
        width: 56px; 
        height: 56px; 
        border-radius: 9999px; 
        display: flex; 
        align-items: center; 
        justify-content: center;
    }
    .kpi-icon-primary { background: #f9dbe5; color: #6f5861; }
    .kpi-icon-secondary { background: #e3e1ec; color: #5d5e66; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon kpi-icon-primary">
                <span class="material-symbols-outlined" style="font-size: 32px;">groups</span>
            </div>
            <div>
                <p style="font-size: 12px; text-transform: uppercase; color: #4e4447; letter-spacing: 0.05em;">סה"כ חברי צוות בפרויקט</p>
                <h3 style="font-size: 24px; font-weight: 600; color: #6f5861;">{total_workers}</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon kpi-icon-secondary">
                <span class="material-symbols-outlined" style="font-size: 32px;">work_history</span>
            </div>
            <div>
                <p style="font-size: 12px; text-transform: uppercase; color: #4e4447; letter-spacing: 0.05em;">סה"כ משרות בפרויקט</p>
                <h3 style="font-size: 24px; font-weight: 600; color: #6f5861;">{total_employment:.0f}%</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # אזור: טבלאות (משאבים פעילים ולא פעילים)
    # ==========================================
    active_df = project_df[project_df['worker_status'].str.strip() == 'פעיל']
    inactive_df = project_df[project_df['worker_status'].str.strip() != 'פעיל']

    st.markdown("""
    <div style="background: #FFFFFF; border-radius: 12px; overflow: hidden; box-shadow: 0px 10px 30px rgba(225, 200, 210, 0.15);">
        <div style="padding: 24px; border-bottom: 1px solid rgba(127, 116, 119, 0.1);">
            <h3 style="font-size: 20px; font-weight: 500; color: #1a1c1c;">רשימת צוות פעילים</h3>
        </div>
    """, unsafe_allow_html=True)

    if len(active_df) > 0:
        st.dataframe(active_df[['worker_name', 'job title', '%_employment', 'notes']], use_container_width=True)
    else:
        st.info("אין חברי צוות פעילים בפרויקט זה.")

    st.markdown("</div>", unsafe_allow_html=True)

    if len(inactive_df) > 0:
        st.markdown("""
        <div style="background: #FFFFFF; border-radius: 12px; overflow: hidden; box-shadow: 0px 10px 30px rgba(225, 200, 210, 0.15); margin-top: 24px;">
            <div style="padding: 24px; border-bottom: 1px solid rgba(127, 116, 119, 0.1);">
                <h3 style="font-size: 20px; font-weight: 500; color: #4e4447;">חברי צוות בעבר (לא פעילים)</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(inactive_df[['worker_name', 'job title', '%_employment', 'notes']], use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
