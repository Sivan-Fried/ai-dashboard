st.markdown("""
<style>
html, body, [class*="css"]  {
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd

st.markdown("""
<style>
body {direction: RTL; text-align: right;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard AI לניהול פרויקטים")

# טעינת נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# הצגה
st.subheader("פרויקטים")
st.dataframe(projects)
st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    if row["status"] == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {row['project_name']}")
    elif row["status"] == "צהוב":
        st.warning(f"⏳ יש לעקוב: {row['project_name']}")
