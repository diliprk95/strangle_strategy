import streamlit as st
import os
import yaml
import time
from kiteconnect import KiteConnect

# Load config
with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

def get_secret(key):
    try:
        # Try Streamlit secrets (Cloud)
        return st.secrets[key]
    except Exception:
        # Fallback to local .env or YAML config
        return os.getenv(key)

api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")
access_token_path =  get_secret("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)

# Set page UI
st.set_page_config(page_title="Zerodha Login")
st.title("🔐 Zerodha Kite Login")

# Query param handling
params = st.query_params
request_token = params.get("request_token")

# SESSION INIT
if "zerodha_logged_in" not in st.session_state:
    st.session_state["zerodha_logged_in"] = False

# CHECK if token already exists
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

# If already logged in
if st.session_state["zerodha_logged_in"] or is_token_valid():
    st.success("✅ You are already logged in to Zerodha.")
    st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")

    if st.button("🔓 Logout"):
        st.session_state["zerodha_logged_in"] = False
        if os.path.exists(access_token_path):
            os.remove(access_token_path)
        st.success("✅ Logged out successfully. Refreshing...")
        time.sleep(1)
        st.rerun()

# Handle callback from Zerodha (i.e., user just logged in)
elif request_token:
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        with open(access_token_path, "w") as f:
            f.write(access_token)

        st.session_state["zerodha_logged_in"] = True
        st.success("✅ Login successful! Redirecting to dashboard...")
        st.st.query_params  # Clear URL params
        time.sleep(2)
        st.switch_page("pages/Strategy_Run.py")

    except Exception as e:
        st.error(f"❌ Login failed: {str(e)}")

# Show login button if not logged in
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
