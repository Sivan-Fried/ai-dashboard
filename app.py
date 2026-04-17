import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard AI לניהול פרויקטים")

projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# התראות
st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    name = row["project_name"]
    status = row["status"]

    if status == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {name}")
    elif status == "צהוב":
        st.warning(f"⏳ יש לעקוב: {name}")
    else:
        st.success(f"✔ תקין: {name}")

# פרויקטים - RTL מלא (כרטיסים בלבד)
st.subheader("📁 פרויקטים")

for _, row in projects.iterrows():
    st.markdown(f"""
<div style="
    direction: rtl;
    text-align: right;
    padding: 14px;
    margin-bottom: 12px;
    border-radius: 12px;
    border: 1px solid #ddd;
    background: #ffffff;
">

### {row['project_name']}
סטטוס: **{row['status']}**

</div>
""", unsafe_allow_html=True)

**פרויקט:** {row['project_name']}  
**סטטוס:** {row['status']}  

</div>
""", unsafe_allow_html=True)
