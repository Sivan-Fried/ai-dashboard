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

# ===== נתונים =====
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

# ===== כרטיסים (RTL אמיתי) =====
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

# ===== Cache פשוט כדי למנוע קריאות חוזרות =====
if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_time" not in st.session_state:
    st.session_state.last_time = 0

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except Exception:
        return "⚠️ עומס על Gemini – נסי שוב בעוד דקה"

# ===== AI =====
st.subheader("🤖 ניתוח AI (Gemini)")

if st.button("נתח פרויקטים עם AI"):

    # הגנה מ־spam (מונע 429)
    if time.time() - st.session_state.last_time < 30:
        st.warning("⏳ חכי 30 שניות בין הרצות AI")
        st.stop()

    st.session_state.last_time = time.time()

    # אם כבר יש תוצאה – לא לקרוא שוב ל־API
    if st.session_state.last_result:
        st.markdown("### תובנות AI (שמורה)")
        st.write(st.session_state.last_result)
        st.stop()

    prompt = f"""
    אתה מנהל פרויקטים בכיר.

    נתוני הפרויקטים:
    {projects.to_string(index=False)}

    תן:
    - סיכום מצב
    - סיכונים
    - מה דורש טיפול מיידי
    בעברית קצרה.
    """

    result = ask_gemini(prompt)
    st.session_state.last_result = result

    st.markdown("### תובנות AI")
    st.write(result)
