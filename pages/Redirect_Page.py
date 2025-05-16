# pages/Redirect_Page.py
import streamlit as st
import os
from kiteconnect import KiteConnect

# --- CONFIG ---
api_key = st.secrets.get("ZERODHA_API_KEY", os.getenv("ZERODHA_API_KEY"))
api_secret = st.secrets.get("ZERODHA_API_SECRET", os.getenv("ZERODHA_API_SECRET"))
access_token_path = st.secrets.get("ZERODHA_ACCESS_TOKEN", os.getenv("ZERODHA_ACCESS_TOKEN"))

st.set_page_config(page_title="Zerodha Redirect", layout="centered")
st.title("🔄 Zerodha Login Callback")

kite = KiteConnect(api_key=api_key)

# --- HANDLE CALLBACK ---
query_params = st.query_params
request_token = query_params.get("request_token")

if not request_token:
    st.error("❌ Missing request_token in URL.")
    st.stop()

try:
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]

    with open(access_token_path, "w") as f:
        f.write(access_token)

    st.success("✅ Login successful! You can close this tab.")
    st.markdown("Return to the original tab — it will detect your login automatically.")
    st.balloons()

except Exception as e:
    st.error(f"❌ Token exchange failed: {e}")
    st.stop()
