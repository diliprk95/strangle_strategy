import streamlit as st
from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
import urllib.parse
import socketserver
import http.server
import threading
import webbrowser

load_dotenv()

api_key = os.getenv("ZERODHA_API_KEY")
api_secret = os.getenv("ZERODHA_API_SECRET")
redirect_uri = "http://localhost:8000"

kite = KiteConnect(api_key=api_key)


def start_redirect_server():
    class TokenHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_path.query)
            request_token = params.get("request_token")[0]
            st.session_state.request_token = request_token

            # Exchange for access_token
            data = kite.generate_session(request_token, api_secret=api_secret)
            access_token = data["access_token"]

            # Save to .env
            with open(".env", "r") as f:
                lines = f.readlines()

            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("ZERODHA_ACCESS_TOKEN="):
                        f.write(f"ZERODHA_ACCESS_TOKEN={access_token}\n")
                    else:
                        f.write(line)

            st.session_state.login_success = True

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Login successful. You can close this tab.</h2>")

    PORT = 8000
    with socketserver.TCPServer(("", PORT), TokenHandler) as httpd:
        httpd.handle_request()


# Streamlit UI
st.set_page_config(page_title="Zerodha Login", layout="centered")
st.title("🔐 Zerodha Kite Login")

if "login_success" not in st.session_state:
    st.session_state.login_success = False

if st.session_state.login_success:
    st.success("✅ Access token saved successfully to `.env`.")
else:
    if st.button("Login to Zerodha"):
        login_url = kite.login_url()
        threading.Thread(target=start_redirect_server, daemon=True).start()
        st.markdown(f"[🔗 Click here to login to Zerodha]({login_url})", unsafe_allow_html=True)
        st.info("Browser opened. After login, access token will be saved.")
