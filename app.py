import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# כותרת
st.title("📊 Dashboard AI לניהול פרויקטים")

# טעינת נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# RTL לטקסטים בלבד (לא טבלאות)
st.markdown("<div dir='rtl' style='text-align:right'>", unsafe_allow_html=True)

st.subheader("פרויקטים")
st.dataframe(projects)

st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    if row["status"] == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {row['project_name']}")
    elif row["status"] == "צהוב":
        st.warning(f"⏳ יש לעקוב: {row['project_name']}")

st.markdown("</div>", unsafe_allow_html=True)
for _, row in projects.iterrows():
    if row["status"] == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {row['project_name']}")
    elif row["status"] == "צהוב":
        st.warning(f"⏳ יש לעקוב: {row['project_name']}")
