import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# כותרת
st.title("📊 Dashboard AI לניהול פרויקטים")

# טעינת נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# RTL לטקסטים בלבד (לא טבלאות)
st.markdown("""
<style>
section.main > div {
    direction: rtl;
}
</style>
""", unsafe_allow_html=True)

st.subheader("פרויקטים")
st.markdown("### פרויקטים")

for _, row in projects.iterrows():
    st.markdown(f"""
    **פרויקט:** {row['project_name']}  
    **סטטוס:** {row['status']}  
    ---
    """)
st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    if row["status"] == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {row['project_name']}")
    elif row["status"] == "צהוב":
        st.warning(f"⏳ יש לעקוב: {row['project_name']}")
