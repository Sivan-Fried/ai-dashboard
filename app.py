import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Dashboard AI לניהול פרויקטים")

projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

st.subheader("פרויקטים")
st.dataframe(projects)

st.subheader("התראות")

for _, row in projects.iterrows():
    if row["status"] == "אדום":
        st.error("פרויקט בסיכון: " + row["project_name"])
    elif row["status"] == "צהוב":
        st.warning("יש לעקוב: " + row["project_name"])
