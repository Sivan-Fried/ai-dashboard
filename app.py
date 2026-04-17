import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# RTL לטקסטים בלבד (יציב)
st.markdown(
    "<div dir='rtl' style='text-align:right'>",
    unsafe_allow_html=True
)

st.title("📊 Dashboard AI לניהול פרויקטים")

# נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# פרויקטים
st.subheader("פרויקטים")
st.dataframe(projects)

# התראות
st.subheader("🚨 התראות")

for _, row in projects.iterrows():
    name = row.get("project_name", "")
    status = row.get("status", "")

    if status == "אדום":
        st.error("⚠️ פרויקט בסיכון: " + name)
    elif status == "צהוב":
        st.warning("⏳ יש לעקוב: " + name)
    else:
        st.success("✔ תקין: " + name)

st.markdown("</div>", unsafe_allow_html=True)
