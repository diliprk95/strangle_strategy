import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from core.zerodha_api import get_kite_client, is_token_valid, get_ltp, get_next_week_expiry
from core.strategy_runner import run_strategy
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Strategy Trigger", layout="wide")
st.title("📈 Run Strangle Strategy")

if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
    st.warning("Please login via Zerodha first.")
    st.stop()

trigger = run_strategy()
st_autorefresh(interval=300000, key="strategy_refresh")  # every 5 minutes

st.write(f"**Status:** {trigger['status']}")
st.write(f"**Time:** {trigger['timestamp']}")

# Validate token
if not is_token_valid():
    st.error("❌ Your Zerodha access token is invalid or expired.")
    st.markdown("[🔑 Click here to re-login](/Zerodha_Login)", unsafe_allow_html=True)
    st.stop()  # Stop further code

# If valid, proceed
kite = get_kite_client()

# Example: Get NIFTY price and next week's expiry
try:
    nifty_price = get_ltp("NIFTY")
    expiry_date = get_next_week_expiry()
    st.success(f"✅ Current NIFTY50 price: ₹{nifty_price}")
    st.success(f"✅ Next week's expiry date: {expiry_date}")
except Exception as e:
    st.error(f"❌ Error fetching data: {e}")

if trigger["status"] == "ENTRY":
    st.success("✅ Entry conditions met!")
    st.write(f"🔹 LTP: {trigger['ltp']}")
    st.write(f"🟢 Buy CE: `{trigger['buy_ce']}`")
    st.write(f"🔴 Buy PE: `{trigger['buy_pe']}`")

elif trigger["status"] == "EXIT":
    st.warning("🚪 Exit signal triggered!")
    st.write(trigger["message"])

else:
    st.info("⌛ Waiting for strategy time window.")
    st.write(trigger["message"])
