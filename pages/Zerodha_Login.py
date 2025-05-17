import streamlit as st
import os
import yaml
import time
from kiteconnect import KiteConnect

# --- Load config ---
with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")
access_token_path = get_secret("ZERODHA_ACCESS_TOKEN") or "access_token.txt"

kite = KiteConnect(api_key=api_key)

# --- Page Setup ---
st.set_page_config(page_title="Zerodha Login", layout="centered")
st.title("🔐 Zerodha Kite Login")

# --- Session State Init ---
if "zerodha_logged_in" not in st.session_state:
    st.session_state["zerodha_logged_in"] = False

# --- Helper Functions ---
def is_token_valid():
    if not os.path.exists(access_token_path):
        return False
    with open(access_token_path, "r") as f:
        token = f.read().strip()
    try:
        kite.set_access_token(token)
        kite.profile()
        return True
    except Exception:
        return False

def mark_logged_in(token: str):
    with open("auth_token.txt", "w") as f:
        f.write(token)

def is_logged_in():
    return os.path.exists("auth_token.txt")

# --- Main Logic ---
params = st.query_params
request_token = params.get("request_token")

# 1. Already Logged In
if is_logged_in() and is_token_valid():
    st.success("✅ Zerodha authenticated.")
    st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")

    if st.button("Logout"):
        for path in ["auth_token.txt", access_token_path]:
            if os.path.exists(path):
                os.remove(path)
        st.success("🔓 Logged out successfully. Please refresh.")

# 2. Handle Callback from Zerodha
elif request_token:
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        with open(access_token_path, "w") as f:
            f.write(access_token)

        mark_logged_in(access_token)
        st.success("✅ Login successful! Redirecting to dashboard...")

        st.query_params.clear()
        time.sleep(2)
        st.switch_page("pages/Strategy_Run.py")

    except Exception as e:
        st.error(f"❌ Login failed: {str(e)}")

# 3. Not Logged In Yet
else:
    login_url = kite.login_url()
    st.markdown(
        f"""
        <a href="{login_url}" target="_blank">
            <button style="padding: 0.6em 1.2em; font-size: 1rem; border-radius: 6px; background-color: #009688; color: white; border: none; cursor: pointer;">
                🔐 Login to Zerodha
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.info("A new tab will open. Login there and come back here.")
