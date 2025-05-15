import os
import threading
import http.server
import socketserver
import urllib.parse
import yaml
import time
import webbrowser
from kiteconnect import KiteConnect
import streamlit as st

# --- CONFIG ---
with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = st.secrets["ZERODHA_API_KEY"]
api_secret = st.secrets["ZERODHA_API_SECRET"]
access_token_path = st.secrets["ZERODHA_ACCESS_TOKEN"]
temp_token_path = "temp_login_token.txt"

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

# Extract request_token from URL
query_params = st.query_params
request_token = query_params.get("request_token")

# --- REDIRECT SERVER HANDLER ---
def start_redirect_server():
    class TokenHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            if "request_token" in params:
                # request_token = params["request_token"][0]
                try:
                    data = kite.generate_session(request_token, api_secret=api_secret)
                    access_token = data["access_token"]

                    # Save access token to main file
                    with open(access_token_path, "w") as f:
                        f.write(access_token)

                    # Touch a temp file to signal Streamlit
                    with open(temp_token_path, "w") as f:
                        f.write("login_success")

                    # Response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    self.end_headers()
                    html_content = """
                    <html>
                        <head><title>Login Success</title></head>
                        <body>
                            <h2>✅Login successful.</h2>
                            <p>You can now return to the app and close this tab.</p>
                        </body>
                    </html>
                    """
                    self.wfile.write(html_content.encode("utf-8"))
                except Exception as e:
                    self.send_error(500, f"Token exchange failed: {e}")
            else:
                self.send_error(400, "Missing request_token")

    PORT = 8000
    with socketserver.TCPServer(("", PORT), TokenHandler) as httpd:
        httpd.handle_request()


# --- SESSION INIT ---
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = is_token_valid()
if "polling_login" not in st.session_state:
    st.session_state.polling_login = False

# --- MAIN UI ---
if st.session_state.is_logged_in:
    st.success("✅ Already authenticated.")
    st.page_link("pages/Strategy_Run.py", label="➡️ Go to Dashboard")

    if st.button("Logout"):
        st.session_state.is_logged_in = False
        if os.path.exists(access_token_path):
            os.remove(access_token_path)
        if os.path.exists(temp_token_path):
            os.remove(temp_token_path)
        st.rerun()

else:
    st.warning("⚠️ You are not logged in to Zerodha.")

    if st.button("🔑 Login to Zerodha"):
        login_url = kite.login_url()
        webbrowser.open_new_tab(login_url)

        # Start redirect server in background
        threading.Thread(target=start_redirect_server, daemon=True).start()
        st.session_state.polling_login = True
        st.info("Opened login tab. Waiting for token...")

    # Polling loop for login success
    if st.session_state.polling_login:
        with st.spinner("Waiting for login response..."):
            for _ in range(30):  # 30 seconds timeout
                if os.path.exists(temp_token_path):
                    if is_token_valid():
                        st.session_state.is_logged_in = True
                        st.session_state.polling_login = False
                        os.remove(temp_token_path)
                        st.success("✅ Login successful!")
                        time.sleep(1)
                        st.rerun()
                time.sleep(1)

        st.error("❌ Login failed or timeout. Please try again.")
        st.session_state.polling_login = False
