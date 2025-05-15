import streamlit as st
from core.config_handler import load_config, save_config
from datetime import datetime

st.title("🛠️ Strategy Settings")

config = load_config()
strategy = config.get("strategy", {})

with st.form("strategy_settings_form"):
    st.subheader("General Strategy Configuration")

    symbol = st.text_input("Symbol", value=strategy.get("symbol", "NIFTY"))

    entry_day = st.selectbox("Entry Day", options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(strategy.get("entry_day", "Friday")))

    # Convert existing string to time object if present
    entry_time_str = strategy.get("entry_time", "10:30")
    entry_time = datetime.strptime(entry_time_str, "%H:%M").time() if isinstance(entry_time_str, str) else entry_time_str
    entry_time = st.time_input("Entry Time", value=entry_time, key="entry_time_input")

    exit_day = st.selectbox("Exit Day", options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(strategy.get("exit_day", "Monday")))

    exit_time_str = strategy.get("exit_time", "13:30")
    exit_time = datetime.strptime(exit_time_str, "%H:%M").time() if isinstance(exit_time_str, str) else exit_time_str
    exit_time = st.time_input("Exit Time", value=exit_time, key="exit_time_input")

    ce_offset = st.number_input("Call Option Offset (pts)", min_value=0, step=50, value=strategy.get("ce_offset", 300))
    pe_offset = st.number_input("Put Option Offset (pts)", min_value=0, step=50, value=strategy.get("pe_offset", 300))
    quantity = st.number_input("Order Quantity", min_value=1, step=1, value=strategy.get("quantity", 50))

    order_enabled = st.checkbox("Enable Auto Order Execution", value=strategy.get("order_enabled", False))

    # Add the missing submit button
    submitted = st.form_submit_button("💾 Save Settings")

    if submitted:
        config["strategy"] = {
            "symbol": symbol,
            "entry_day": entry_day,
            "entry_time": entry_time.strftime("%H:%M"),
            "exit_day": exit_day,
            "exit_time": exit_time.strftime("%H:%M"),
            "ce_offset": ce_offset,
            "pe_offset": pe_offset,
            "quantity": quantity,
            "order_enabled": order_enabled,
        }
        save_config(config)
        st.success("✅ Strategy settings saved successfully!")
