import streamlit as st
import pandas as pd

st.markdown("""
<style>
body {direction: RTL; text-align: right;}
</style>
""", unsafe_allow_html=True)

st.title("הדשבורד שלי")

# טעינת נתונים
import os
projects = pd.read_excel(os.path.join(os.path.dirname(__file__), "projects.xlsx"), engine="openpyxl")

# הצגה
st.subheader("פרויקטים")
st.dataframe(projects)
