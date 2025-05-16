# pages/Redirect_Page.py
import streamlit as st
import os
from kiteconnect import KiteConnect
import urllib.parse

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")
access_token_path = get_secret("ZERODHA_ACCESS_TOKEN")

st.set_page_config(page_title="Zerodha Redirect", layout="centered")
st.title("🔁 Zerodha Callback Handler")

kite = KiteConnect(api_key=api_key)

# Extract request_token
query_params = st.query_params
request_token = query_params.get("request_token")

if request_token:
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        with open(access_token_path, "w") as f:
            f.write(access_token)

        st.success("✅ Login successful!")
        st.info("You can close this tab and return to the main app.")
    except Exception as e:
        st.error(f"❌ Token exchange failed: {e}")
else:
    st.warning("⚠️ No `request_token` found in URL.")
