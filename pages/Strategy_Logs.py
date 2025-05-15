# streamlit_app/pages/📜 Strategy_Logs.py

import os
import json
import streamlit as st

st.set_page_config(page_title="📜 Strategy Logs", layout="wide")
st.title("📜 Strategy Log Viewer")

log_path = "logs/strategy_log.jsonl"
manual_log_path = "logs/manual_trigger.log"

# ---- Strategy Logs ----
st.subheader("📘 Strategy Execution Logs")

if not os.path.exists(log_path):
    st.info("No strategy logs found yet. Run the strategy to generate logs.")
else:
    logs = []
    with open(log_path, "r") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if logs:
        logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
        st.markdown(f"### Total strategy logs: {len(logs)}")

        for log in logs[:100]:
            status = log.get("status")
            timestamp = log.get("timestamp")
            message = log.get("message", "")
            ltp = log.get("ltp", "-")
            ce = log.get("buy_ce", "-")
            pe = log.get("buy_pe", "-")

            with st.expander(f"{timestamp} — {status}"):
                st.write(f"**Message:** {message}")
                if status in ["ENTRY", "EXIT", "WAIT", "ERROR"]:
                    st.write(f"**LTP:** ₹{ltp}")
                    st.write(f"🔹 Buy CE: `{ce}`")
                    st.write(f"🔴 Buy PE: `{pe}`")
    else:
        st.warning("Strategy log file is empty.")

# ---- Manual Trigger Logs ----
st.divider()
st.subheader("🧪 Manual Trigger Logs")

if not os.path.exists(manual_log_path):
    st.info("No manual actions logged yet.")
else:
    with open(manual_log_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        st.warning("Manual trigger log is empty.")
    else:
        for entry in reversed(lines[-50:]):  # Show last 50
            st.markdown(f"🔸 `{entry}`")
    