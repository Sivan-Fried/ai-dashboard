import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# כותרת
st.title("📊 Dashboard AI לניהול פרויקטים")

# טעינת נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# פרויקטים (תצוגה פשוטה שעובדת טוב)
st.subheader("פרויקטים")

for _, row in projects.iterrows():
    st.markdown(f"""
**פרויקט:** {row['project_name']}  
**סטטוס:** {row['status']}  
---
""")

# התראות
st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    if row["status"] == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {row['project_name']}")
    elif row["status"] == "צהוב":
        st.warning(f"⏳ יש לעקוב: {row['project_name']}")
