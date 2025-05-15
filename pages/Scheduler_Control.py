# streamlit_app/pages/📅 Scheduler_Control.py

import streamlit as st
import time
from core.scheduler import start_scheduler, stop_scheduler, is_scheduler_running
from core.config_handler import load_config, save_config
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="📅 Scheduler Control", layout="centered")
st.title("📅 Scheduler Control Panel")

if "scheduler_running" not in st.session_state:
    st.session_state.scheduler_running = is_scheduler_running()

config = load_config()
interval = config.get("scheduler", {}).get("interval_minutes", 1)

st.markdown(f"### Current Interval: `{interval}` minute(s)")
running = is_scheduler_running()

# Show persistent status message if present, and auto-hide after 5 seconds
if (
    "scheduler_status_msg" in st.session_state
    and "msg_time" in st.session_state
):
    st_autorefresh(interval=1000, key="auto_refresh")  # Refresh every 1 second
    st.success(st.session_state.scheduler_status_msg)
    if time.time() - st.session_state.msg_time > 5:
        del st.session_state.scheduler_status_msg
        del st.session_state.msg_time
        st.rerun()

col1, col2 = st.columns(2)
with col1:
    new_interval = st.number_input("Set Interval (minutes)", min_value=1, max_value=60, value=interval, step=1)
with col2:
    if st.session_state.scheduler_running:
        if st.button("🛑 Stop Scheduler"):
            stop_scheduler()
            st.session_state.scheduler_running = False
            st.session_state.scheduler_status_msg = "✅ Scheduler stopped"
            st.session_state.msg_time = time.time()
            st.rerun()
    else:
        if st.button("▶️ Start Scheduler"):
            start_scheduler()
            st.session_state.scheduler_running = True
            st.session_state.scheduler_status_msg = "✅ Scheduler started"
            st.session_state.msg_time = time.time()
            st.rerun()

# Save updated interval
if new_interval != interval:
    config["scheduler"] = config.get("scheduler", {})
    config["scheduler"]["interval_minutes"] = new_interval
    save_config(config)
    st.info("⏱ Interval saved. Restart scheduler to apply changes.")
