import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard AI לניהול פרויקטים")

projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    name = row.get("project_name", "")
    status = row.get("status", "")

    if status == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {name}")
    elif status == "צהוב":
        st.warning(f"⏳ יש לעקוב: {name}")
    else:
        st.success(f"✔ תקין: {name}")

st.subheader("📁 פרויקטים")

st.dataframe(projects, use_container_width=True)
