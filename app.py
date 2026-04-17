import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

st.markdown("<h2 style='text-align:center'>📊 Dashboard AI לניהול פרויקטים</h2>", unsafe_allow_html=True)

projects = pd.read_excel("my_projects.xlsx", engine="openpyxl")

# =========================
# Gemini
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(prompt):
    return model.generate_content(prompt).text

# =========================
# התראות
# =========================
st.markdown("### 🚨 התראות")

for _, row in projects.iterrows():
    status = row["status"]

    color = "#e6ffe6" if status == "ירוק" else "#fff7e6" if status == "צהוב" else "#ffe5e5"

    st.markdown(
        "<div style='direction:rtl;text-align:right;padding:10px;margin-bottom:6px;"
        f"border-radius:10px;background:{color};border:1px solid #ddd'>"
        f"<b>{row['project_name']}</b><br>{status}</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# =========================
# פרויקטים
# =========================
st.markdown("### 📁 פרויקטים")
st.dataframe(projects, use_container_width=True)

st.markdown("---")

# =========================
# AI
# =========================
st.markdown("### 🤖 אזור AI")

project = st.selectbox("בחרי פרויקט", projects["project_name"].tolist())
question = st.text_area("שאלה")

run = st.button("שלח ל-AI")

if run:

    row = projects[projects["project_name"] == project].iloc[0]

    context = projects.to_string(index=False)

    prompt = (
        "נתוני פרויקטים:\n"
        f"{context}\n\n"
        "פרויקט נבחר:\n"
        f"{row['project_name']} - {row['status']}\n\n"
        "שאלה:\n"
        f"{question}\n"
    )

    result = ask_gemini(prompt)

    st.markdown("### תשובת AI")

    st.markdown(
        "<div style='direction:rtl;text-align:right;padding:14px;"
        "border-radius:10px;background:#fafafa;border:1px solid #ddd;white-space:pre-wrap'>"
        f"{result}</div>",
        unsafe_allow_html=True
    )
