import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# כותרת ממורכזת
st.markdown(
    "<h1 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h1>",
    unsafe_allow_html=True
)

# טעינת נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# התראות
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

# פרויקטים
st.subheader("📁 פרויקטים")
st.dataframe(projects, use_container_width=True)
