import streamlit as st
import pandas as pd
import os
import time
import google.generativeai as genai

st.set_page_config(layout="wide")

# ===== כותרת =====
st.markdown(
    "<h1 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h1>",
    unsafe_allow_html=True
)

# ===== טעינת נתונים =====
projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# ===== התראות =====
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

# ===== פרויקטים (כרטיסים RTL) =====
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

# ===== Gemini setup =====
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# ===== הגנה מ-Quota =====
if "last_run" not in st.session_state:
    st.session_state.last_run = 0

st.subheader("🤖 ניתוח AI (Gemini)")

if st.button("נתח פרויקטים עם AI"):

    # הגנה מפני לחיצות מהירות
    if time.time() - st.session_state.last_run < 20:
        st.warning("⏳ חכי כמה שניות לפני הרצה נוספת")
        st.stop()

    st.session_state.last_run = time.time()

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

    result = ask_gemini(prompt)

    st.markdown("### תובנות AI")
    st.write(result)
