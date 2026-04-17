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
    name = row.get("project_name", "")
    status = row.get("status", "")

    if status == "אדום":
        st.error(f"⚠️ פרויקט בסיכון: {name}")
    elif status == "צהוב":
        st.warning(f"⏳ יש לעקוב: {name}")
    else:
        st.success(f"✔ תקין: {name}")

# ===== טבלת פרויקטים =====
st.subheader("📁 פרויקטים")
st.dataframe(projects, use_container_width=True)

# ===== Gemini setup =====
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except Exception:
        return "⚠️ שגיאה או עומס על Gemini – נסי שוב בעוד דקה"

# =========================
# ניתוח פרויקט ספציפי
# =========================
st.subheader("🎯 ניתוח פרויקט")

project_names = projects["project_name"].tolist()
selected_project = st.selectbox("בחרי פרויקט", project_names)

if st.button("נתח פרויקט"):
    row = projects[projects["project_name"] == selected_project].iloc[0]

    prompt = f"""
    את מומחית לניהול פרויקטים.

    נתחי את הפרויקט:

    שם: {row['project_name']}
    סטטוס: {row['status']}

    תני:
    - סיכון
    - בעיות
    - המלצה
    בעברית קצרה וברורה
    """

    result = ask_gemini(prompt)
    st.markdown("### 🤖 תובנות AI")
    st.write(result)

# =========================
# צ'אט חופשי עם הקשר מלא
# =========================
st.subheader("💬 שיחה חופשית עם AI")

user_question = st.text_area("שאלי שאלה חופשית על הפרויקטים")

if st.button("שלח ל-AI"):

    if user_question.strip() == "":
        st.warning("כתבי שאלה קודם")
    else:

        # הקשר מלא של הדאטה
        projects_context = projects.to_string(index=False)

        prompt = f"""
        את עוזרת לניהול פרויקטים בכירה.

        הנה כל הנתונים:
        {projects_context}

        שאלה:
        {user_question}

        תעני בעברית קצרה, ברורה ומעשית.
        """

        result = ask_gemini(prompt)
        st.markdown("### 💡 תשובת AI")
        st.write(result)
