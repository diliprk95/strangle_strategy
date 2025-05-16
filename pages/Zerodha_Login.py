import os
import socket
import yaml
import streamlit as st
from kiteconnect import KiteConnect
from urllib.parse import urlencode

# Load config values
with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key) or config.get(key)

api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")
access_token_path = get_secret("ZERODHA_ACCESS_TOKEN") or "access_token.txt"

# Determine environment
hostname = socket.gethostname()
is_local = "localhost" in st.request.url or "127.0.0.1" in st.request.url

st.set_page_config(page_title="Zerodha Login", layout="centered")
st.title("🔐 Zerodha Kite Login")

kite = KiteConnect(api_key=api_key)

def is_token_valid():
    try:
        if not os.path.exists(access_token_path):
            return False
        with open(access_token_path, "r") as f:
            token = f.read().strip()
        kite.set_access_token(token)
        kite.profile()
        return True
    except:
        return False

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = is_token_valid()

# Detect request_token from query (Streamlit Cloud)
query_params = st.query_params
if "request_token" in query_params:
    request_token = query_params["request_token"]
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        with open(access_token_path, "w") as f:
            f.write(access_token)
        st.session_state.is_logged_in = True
        st.success("✅ Login successful!")
        st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")
        st.stop()
    except Exception as e:
        st.error(f"❌ Token exchange failed: {str(e)}")

# MAIN UI
if st.session_state.is_logged_in:
    st.success("✅ You are logged in to Zerodha.")
    st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")
    if st.button("Logout"):
        st.session_state.is_logged_in = False
        if os.path.exists(access_token_path):
            os.remove(access_token_path)
        st.rerun()
else:
    st.warning("⚠️ You are not logged in.")

    # Determine login URL
    if is_local:
        # Local dev environment
        redirect_uri = "http://localhost:8000"
    else:
        # Deployed Streamlit app
        redirect_uri = "https://stranglestrategy.streamlit.app/Zerodha_Login"

    # Override redirect URI
    login_url = kite.login_url() + f"&redirect_uri={redirect_uri}"
    st.markdown(f"[🔑 Click here to login to Zerodha]({login_url})", unsafe_allow_html=True)
