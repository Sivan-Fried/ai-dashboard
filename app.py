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
