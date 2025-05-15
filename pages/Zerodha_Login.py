import os
import streamlit as st
import yaml
from kiteconnect import KiteConnect
import time
import urllib.parse
import webbrowser

# --- LOCAL DEV REDIRECT SERVER (commented for cloud) ---
# import threading
# import http.server
# import socketserver

def get_secret(key):
    try:
        # Try Streamlit secrets (Cloud)
        return st.secrets[key]
    except Exception:
        # Fallback to local .env or YAML config
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


# --- SESSION INIT ---
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = is_token_valid()


# --- STREAMLIT CLOUD FLOW ---
query_params = st.query_params
request_token = query_params.get("request_token")

if request_token and "callback" in query_params:
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        # Save access token
        with open(access_token_path, "w") as f:
            f.write(access_token)

        st.session_state.is_logged_in = True
        st.markdown("### ✅ Login successful! You can close this tab.")
        st.stop()
        st.query_params  # Clear query params
        st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")
    except Exception as e:
        st.error(f"Token exchange failed: {e}")
        st.stop()

elif st.session_state.is_logged_in:
    st.success("✅ Already authenticated.")
    st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")

    if st.button("Logout"):
        st.session_state.is_logged_in = False
        if os.path.exists(access_token_path):
            os.remove(access_token_path)
        st.rerun()

else:
    st.warning("⚠️ You are not logged in to Zerodha.")
    login_url = kite.login_url()
    is_local = os.getenv("IS_LOCAL", "0") == "1"

    if is_local:
        if st.button("🔑 Login to Zerodha"):
            webbrowser.open_new_tab(login_url)
            st.info("Opened Zerodha login page in a new tab. You'll be redirected back here with access.")
    else:
       login_url = kite.login_url()
       login_url_with_callback = login_url + "&callback=1"
       st.link_button("🔑 Login to Zerodha", login_url_with_callback)
       st.info("You'll be redirected back here with access.")

    # --- LOCALHOST REDIRECT FLOW (FOR LOCAL DEV ONLY) ---
    # """
    # To use local redirect server, uncomment this section and run locally:

    # # import webbrowser
    # # import threading

    # def start_redirect_server():
    #     class TokenHandler(http.server.SimpleHTTPRequestHandler):
    #         def do_GET(self):
    #             parsed = urllib.parse.urlparse(self.path)
    #             params = urllib.parse.parse_qs(parsed.query)
    #             if "request_token" in params:
    #                 try:
    #                     data = kite.generate_session(params["request_token"][0], api_secret=api_secret)
    #                     access_token = data["access_token"]
    #                     with open(access_token_path, "w") as f:
    #                         f.write(access_token)
    #                     self.send_response(200)
    #                     self.end_headers()
    #                     self.wfile.write(b"<h2>✅ Login successful. You can close this tab.</h2>")
    #                 except Exception as e:
    #                     self.send_error(500, f"Token exchange failed: {e}")
    #             else:
    #                 self.send_error(400, "Missing request_token")

    #     PORT = 8000
    #     with socketserver.TCPServer(("", PORT), TokenHandler) as httpd:
    #         httpd.handle_request()

    # # For local development:
    # if st.button("🔑 Login Locally"):
    #     webbrowser.open_new_tab(kite.login_url())
    #     threading.Thread(target=start_redirect_server, daemon=True).start()
    #     st.info("Opened browser tab. Waiting for token...")
    # """

