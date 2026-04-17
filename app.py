import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(layout="wide")

# ===== Gemini setup =====
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

# ===== UI =====
st.markdown(
    "<h1 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h1>",
    unsafe_allow_html=True
)

# טעינת נתונים
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# ===== התראות AI =====
st.subheader("🤖 התראות AI (Gemini)")

if st.button("נתח פרויקטים"):
    prompt = f"""
    אתה עוזר לניהול פרויקטים.

    הנה נתוני הפרויקטים:
    {projects.to_string(index=False)}

    תן:
    - סיכום מצב
    - סיכונים
    - מה דורש טיפול מיידי
    קצר וברור בעברית.
    """

    result = ask_gemini(prompt)
    st.write(result)

# ===== התראות רגילות =====
st.subheader("🚨 התראות מהירות")

for _, row in projects.iterrows():
    name = row.get("project_name", "")
    status = row.get("status", "")

    if status == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {name}")
    elif status == "צהוב":
        st.warning(f"⏳ יש לעקוב: {name}")
    else:
        st.success(f"✔ תקין: {name}")

# ===== טבלה =====
st.subheader("📁 פרויקטים")
st.dataframe(projects, use_container_width=True)
