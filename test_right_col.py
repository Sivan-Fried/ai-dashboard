import streamlit as st

# עיצוב בסיסי
st.set_page_config(page_title="עוזר ה‑AI שלך", layout="wide")

# CSS פנימי — Streamlit תמיד מרנדר אותו
st.markdown("""
<style>
.ai-box {
    background-color: #ffe6f2;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ffb6d5;
    direction: rtl;
}

.ai-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.ai-header h4 {
    margin: 0;
    font-size: 22px;
    color: #d63384;
}

.ai-description {
    margin-top: 10px;
    font-size: 16px;
    color: #444;
}

.ai-input {
    margin-top: 20px;
}

button[kind="primary"] {
    background-color: #ff66a3 !important;
    color: white !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# מבנה החלונית
with st.container():
    st.markdown('<div class="ai-box">', unsafe_allow_html=True)

    st.markdown("""
    <div class="ai-header">
        <span style="font-size:28px;">🤖</span>
        <h4>עוזר ה‑AI שלך</h4>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p class="ai-description">
        דברי על הפרויקטים שלך או צרי משימה חדשה
    </p>
    """, unsafe_allow_html=True)

    # בחירה
    option = st.selectbox("בחרי פרויקט", ["כללי - כל הפרויקטים", "פרויקט 1", "פרויקט 2"])

    # שדה טקסט
    user_input = st.text_input("איך אוכל לעזור?", "")

    # כפתור
    if st.button("שגרי שאילתה 🚀"):
        st.success("הבקשה נשלחה!")

    st.markdown('</div>', unsafe_allow_html=True)
