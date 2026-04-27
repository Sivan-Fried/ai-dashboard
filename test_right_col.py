import streamlit as st

# --- CSS לנראות ---
st.markdown("""
<style>
.ai-box {
    background-color: #FADCE6;
    padding: 24px;
    border-radius: 24px;
    box-shadow: 0px 10px 30px rgba(225,200,210,0.25);
    direction: rtl;
    margin-bottom: 20px;
}
.ai-title {
    font-size: 20px;
    font-weight: 600;
    color: #6f5861;
    margin: 0;
}
.ai-desc {
    font-size: 14px;
    color: #6f5861;
    opacity: 0.85;
    margin-bottom: 16px;
}
.ai-send {
    background-color: #6f5861;
    color: white;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-top: -50px;
    margin-right: 10px;
    float: left;
}
</style>
""", unsafe_allow_html=True)

# --- כרטיס AI ---
st.markdown('<div class="ai-box">', unsafe_allow_html=True)

st.markdown('<p class="ai-title">🤖 עוזר ה‑AI שלך</p>', unsafe_allow_html=True)
st.markdown('<p class="ai-desc">שאלי אותי כל דבר על הפרויקטים שלך או צרי משימה חדשה.</p>', unsafe_allow_html=True)

project = st.selectbox("", ["כללי - כל הפרויקטים", "AnalystCustomers", "IDI App"])
question = st.text_area("", placeholder="איך אוכל לעזור?", height=130)

st.markdown('<div class="ai-send">
