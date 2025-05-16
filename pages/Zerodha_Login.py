# pages/Zerodha_Login.py
import streamlit as st
import os
import time
from kiteconnect import KiteConnect

# --- SECRET HELPER ---
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

# --- CONFIG ---
api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")
access_token_path = get_secret("ZERODHA_ACCESS_TOKEN")

st.set_page_config(page_title="Zerodha Login", layout="centered")
st.title("🔐 Zerodha Kite Login")

kite = KiteConnect(api_key=api_key)

# --- TOKEN VALIDATION ---
def is_token_valid():
    if not os.path.exists(access_token_path):
        return False
    try:
        with open(access_token_path, "r") as f:
            token = f.read().strip()
        kite.set_access_token(token)
        kite.profile()
        return True
    except:
        return False

# --- SESSION STATE ---
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = is_token_valid()

if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

# --- MAIN LOGIN LOGIC ---
if st.session_state.is_logged_in:
    st.success("✅ Logged in successfully.")
    st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")

    if st.button("Logout"):
        st.session_state.is_logged_in = False
        if os.path.exists(access_token_path):
            os.remove(access_token_path)
        st.rerun()

else:
    st.warning("⚠️ You are not logged in to Zerodha.")
    login_url = kite.login_url()
    redirect_url = f"{login_url}&redirect_url=https://stranglestrategy.streamlit.app/pages/Redirect_Page"

    st.link_button("🔑 Login to Zerodha (opens in new tab)", redirect_url)

    if st.button("Start Login Check"):
        st.session_state.login_attempted = True
        st.rerun()

    if st.session_state.login_attempted:
        st.info("Waiting for login to complete in new tab...")

        countdown_placeholder = st.empty()
        with st.spinner("⏳ Checking login status..."):
            for i in reversed(range(30)):
                countdown_placeholder.info(f"⏳ Checking again in {i} seconds...")
                time.sleep(1)
                if is_token_valid():
                    st.session_state.is_logged_in = True
                    st.rerun()
        
        countdown_placeholder.warning("❌ Login not detected.")
        st.session_state.login_attempted = False
        if st.button("🔁 Retry"):
            st.session_state.login_attempted = True
            st.rerun()
