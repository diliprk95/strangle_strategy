import streamlit as st
from core.scheduler import start_scheduler

st.set_page_config(page_title="Options Strangle Strategy", layout="wide")

# Start the background scheduler only once
if "scheduler_started" not in st.session_state:
    start_scheduler()
    st.session_state["scheduler_started"] = True

st.switch_page("pages/Zerodha_Login.py")
st.title("📊 Options Strangle Strategy Dashboard")

st.markdown("""
Welcome to the dashboard. Use the sidebar to navigate.
""")
