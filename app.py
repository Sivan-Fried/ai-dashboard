import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# RTL לכל הטקסטים (מה שעובד באמת ב-Streamlit)
st.markdown(
    """
    <style>
    .main {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# כותרת
st.title("📊 Dashboard AI לניהול פרויקטים")

# נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# טבלה (תישאר LTR - מגבלה של Streamlit)
st.subheader("פרויקטים")
st.dataframe(projects, use_container_width=True)

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
