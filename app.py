import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# ===== Gemini setup (from Streamlit Secrets) =====
import google.generativeai as genai

for m in genai.list_models():
    print(m.name)
    
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

# ===== UI =====
st.markdown(
    "<h1 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h1>",
    unsafe_allow_html=True
)

# ===== Load data =====
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# ===== AI Analysis =====
st.subheader("🤖 ניתוח AI (Gemini)")

if st.button("נתח פרויקטים"):
    prompt = f"""
    אתה מנהל פרויקטים בכיר.

    הנה נתוני הפרויקטים:
    {projects.to_string(index=False)}

    תן:
    - סיכום מצב כללי
    - סיכונים מרכזיים
    - מה דורש טיפול מיידי
    תשובה קצרה וברורה בעברית.
    """

    result = ask_gemini(prompt)
    st.write(result)

# ===== Alerts =====
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

# ===== Table =====
st.subheader("📁 פרויקטים")
st.dataframe(projects, use_container_width=True)
