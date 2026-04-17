import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard AI לניהול פרויקטים")

# טעינת נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# טבלת פרויקטים (יציב + קריא)
st.subheader("פרויקטים")
st.dataframe(projects, use_container_width=True)

# התראות
st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    status = row.get("status", "")

    if status == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {row.get('project_name', '')}")
    elif status == "צהוב":
        st.warning(f"⏳ יש לעקוב: {row.get('project_name', '')}")
    else:
        st.success(f"✔ תקין: {row.get('project_name', '')}")
