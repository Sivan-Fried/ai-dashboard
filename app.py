import streamlit as st
import pandas as pd

st.markdown("""
<style>
body {direction: RTL; text-align: right;}
</style>
""", unsafe_allow_html=True)

st.title("הדשבורד שלי")

# טעינת נתונים
projects = pd.read_excel("projects.xlsx", engine="openpyxl")

# הצגה
st.subheader("פרויקטים")
st.dataframe(projects)
