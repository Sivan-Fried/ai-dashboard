import streamlit as st

st.set_page_config(layout="centered")

# CSS מלא שמייצר את העיצוב מהתמונה
st.markdown("""
<style>
/* קונטיינר ורוד */
.ai-box {
    background-color: #FADCE6;
    padding: 24px;
    border-radius: 24px;
    width: 100%;
    max-width: 400px;
    margin: auto;
    box-shadow: 0px 10px 30px rgba(225,200,210,0.25);
    direction: rtl;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* כותרת */
.ai-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}

.ai-header h4 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #6f5861;
}

/* טקסט תיאור */
.ai-description {
    font-size: 14px;
    color: #6f5861;
    opacity: 0.85;
    margin-bottom: 20px;
    text-align: right;
}

/* תיבת בחירה */
select {
    width: 100%;
    background: rgba(255,255,255,0.6);
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-size: 14px;
    text-align: right;
    outline: none;
}

/* טקסטבוקס */
textarea {
    width: 100%;
    background: white;
    border: none;
    border-radius: 18px;
    padding: 14px;
    height: 120px;
    font-size: 14px;
    resize: none;
    outline: none;
}

/* כפתור עגול */
.send-btn {
    position: absolute;
    left: 12px;
    bottom: 12px;
    width: 42px;
    height: 42px;
    background-color: #6f5861;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    cursor: pointer;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# HTML של הקומפוננטה
st.markdown("""
<div class="ai-box">

    <div class="ai-header">
        <span style="font-size:26px;">🤖</span>
        <h4>עוזר ה‑AI שלך</h4>
    </div>

    <p class="ai-description">
        שאל אותי כל דבר על הפרויקטים שלך או צור משימה חדשה.
    </p>

    <div style="margin-bottom: 16px;">
        <select>
            <option>בחר פרויקט לניתוח...</option>
            <option>מיתוג מחדש - Aura 2.0</option>
            <option>קמפיין השקה חורף</option>
        </select>
    </div>

    <div style="position: relative;">
        <textarea placeholder="איך אוכל לעזור?"></textarea>
        <div class="send-btn">←</div>
    </div>

</div>
""", unsafe_allow_html=True)
