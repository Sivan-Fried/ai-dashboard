# -*- coding: utf-8 -*-
import streamlit as st


def show_tasks_page(project_name=None):
    title = f"משימות — {project_name}" if project_name else "משימות"
    st.markdown(f"### {title}", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#a1a1aa;margin-top:-4px;"
        "text-align:right;padding-right:18px;'>ניהול ומעקב משימות לפרויקט</p>",
        unsafe_allow_html=True,
    )
    st.write("תוכן יתווסף בהמשך")
