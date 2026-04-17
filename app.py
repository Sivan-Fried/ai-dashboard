import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard AI לניהול פרויקטים")

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

# פרויקטים (RTL אמיתי דרך כרטיסים)
st.subheader("📁 פרויקטים")

for _, row in projects.iterrows():
    st.markdown(f"""
<div style="
    text-align: right;
    direction: rtl;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 10px;
    margin-bottom: 10px;
    background-color: #fafafa;
">

**פרויקט:** {row['project_name']}  
**סטטוס:** {row['status']}  

</div>
""", unsafe_allow_html=True)
