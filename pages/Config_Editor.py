import streamlit as st
from datetime import datetime
from core.config_handler import load_config, save_config
from core.zerodha_api import get_kite_client, get_ltp, get_next_week_expiry

config = load_config()
strategy = config["strategy"]
st.set_page_config(page_title="Config Editor", layout="wide")
st.title("⚙️ Strategy Configuration Editor")
st.markdown("### 📊 Active Strategy Config")
st.info(f"""
🔹 **Symbol:** `{strategy.get('symbol', 'NIFTY')}`  
📆 **Entry:** `{strategy.get('entry_day', 'Friday')} at {strategy.get('entry_time', '10:30')}`  
📆 **Exit:** `{strategy.get('exit_day', 'Monday')} at {strategy.get('exit_time', '15:00')}`  
🎯 **Strike Distance:** `{strategy.get('strike_distance', 300)}`  
📦 **Quantity:** `{strategy.get('quantity', 50)}`  
🛒 **Orders Enabled:** `{"Yes" if strategy.get('order_enabled') else "No"}`
""")
# Utility to parse time safely
def parse_time(t):
    return datetime.strptime(t, "%H:%M").time() if isinstance(t, str) else t

# Optional: Log manual actions
def log_manual_action(action):
    with open("logs/manual_trigger.log", "a") as f:
        f.write(f"{datetime.now()} - {action}\n")

config = load_config()
strategy = config.get("strategy", {})

st.divider()
st.subheader("🧪 Manual Strategy Trigger (Override Time Check)")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Force Entry Now"):
        ce = pe = None
        try:
            symbol = strategy.get("symbol", "NIFTY")
            ltp = get_ltp(symbol)
            expiry = get_next_week_expiry()
            strike_distance = strategy.get("strike_distance", 300)
            quantity = strategy.get("quantity", 50)

            rounded_price = round(ltp / 50) * 50
            ce = f"{symbol}{expiry}C{rounded_price + strike_distance}"
            pe = f"{symbol}{expiry}P{rounded_price - strike_distance}"
            st.info(f"Entry Symbols → 🔹 CE: `{ce}` 🔹 PE: `{pe}`")

            kite = get_kite_client()
            ce_order = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NFO,
                tradingsymbol=ce,
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                quantity=quantity,
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_MIS
            )
            pe_order = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NFO,
                tradingsymbol=pe,
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                quantity=quantity,
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_MIS
            )
            st.success(f"✅ Manual Entry Orders Placed:\n\n🔹 CE: {ce_order}\n🔹 PE: {pe_order}")
            log_manual_action(f"Force Entry - CE: {ce_order}, PE: {pe_order}")
        except Exception as e:
            st.error(f"❌ Manual Entry Failed: {e}")

with col2:
    if st.button("❌ Force Exit (Notify only)"):
        st.warning("🟡 Manual exit triggered — please square off positions manually via broker.")
        log_manual_action("Manual Exit Triggered")

# --- Editable Form ---
st.subheader("Strategy Parameters")
with st.form("config_form"):

    symbol = st.text_input("Symbol", strategy.get("symbol", "NIFTY"))
    entry_day = st.selectbox("Entry Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], 
                             index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(strategy.get("entry_day", "Friday")))
    entry_time = st.time_input("Entry Time", value=parse_time(strategy.get("entry_time", "10:30")))

    exit_day = st.selectbox("Exit Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], 
                            index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(strategy.get("exit_day", "Monday")))
    exit_time = st.time_input("Exit Time", value=parse_time(strategy.get("exit_time", "15:00")))

    strike_distance = st.number_input("Strike Distance", value=strategy.get("strike_distance", 300), step=50)
    quantity = st.number_input("Quantity", value=strategy.get("quantity", 50), step=1)
    order_enabled = st.checkbox("Enable Order Placement", value=strategy.get("order_enabled", False))

    submitted = st.form_submit_button("💾 Save Config")
    if submitted:
         # Validate fields
        errors = []

        if not symbol.strip():
            errors.append("❌ Symbol cannot be empty.")
        if quantity <= 0:
            errors.append("❌ Quantity must be greater than zero.")
        if strike_distance < 50:
            errors.append("❌ Strike distance should be at least 50.")
        if entry_day == exit_day and entry_time >= exit_time:
            errors.append("❌ Entry time must be before exit time on the same day.")

        if errors:
            for err in errors:
                st.error(err)
            st.stop()

        # Save after validation
        strategy.update({
            "symbol": symbol,
            "entry_day": entry_day,
            "entry_time": entry_time.strftime("%H:%M") if hasattr(entry_time, "strftime") else entry_time,
            "exit_day": exit_day,
            "exit_time": exit_time.strftime("%H:%M") if hasattr(exit_time, "strftime") else exit_time,
            "strike_distance": strike_distance,
            "quantity": quantity,
            "order_enabled": order_enabled
        })
        config["strategy"] = strategy
        save_config(config)
        st.success("✅ Configuration saved successfully.")
        log_manual_action("Configuration Updated")
