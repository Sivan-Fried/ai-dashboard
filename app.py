import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# ===== כותרת =====
st.markdown(
    "<h1 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h1>",
    unsafe_allow_html=True
)

# ===== נתונים =====
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# ===== התראות =====
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

# ===== פרויקטים (RTL כרטיסים) =====
st.subheader("📁 פרויקטים")

for _, row in projects.iterrows():
    st.markdown(f"""
<div style="
    direction: rtl;
    text-align: right;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 12px;
    margin-bottom: 10px;
    background-color: #fafafa;
">

**פרויקט:** {row['project_name']}  
**סטטוס:** {row['status']}  

</div>
""", unsafe_allow_html=True)

# ===== Gemini AI =====
st.subheader("🤖 ניתוח AI (Gemini)")

if st.button("נתח פרויקטים עם AI"):

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    אתה מנהל פרויקטים בכיר.

    הנה הנתונים:
    {projects.to_string(index=False)}

    תן:
    - סיכום מצב
    - סיכונים
    - מה דורש טיפול מיידי
    בעברית, קצר וברור.
    """

    response = model.generate_content(prompt)

    st.markdown("### תובנות AI")
    st.write(response.text)
