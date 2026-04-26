# -*- coding: utf-8 -*-

# =========================================================
# ייבוא ספריות
# =========================================================
import streamlit as st
import requests
import pandas as pd
import base64
import datetime
import urllib.parse
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components
import google.generativeai as genai
from streamlit_js_eval import get_geolocation
from workplan_module import build_timeline_html
from urllib.parse import urlencode

# הגדרות דף
st.set_page_config(
    layout="wide",
    page_title="Dashboard Sivan",
    initial_sidebar_state="collapsed"
)

# טעינת פונטים
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" />', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0"/>', unsafe_allow_html=True)

# טעינת CSS חיצוני
with open("styles_v2.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- כאן מתחיל הדשבורד שלך ---
st.markdown("<h1 class='dashboard-header'>AURA Dashboard</h1>", unsafe_allow_html=True)

st.write("כאן תמשיכי לבנות את הדשבורד החדש שלך...")

