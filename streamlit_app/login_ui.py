import streamlit as st
from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
import urllib.parse
import socketserver
import http.server
import threading

load_dotenv()

# Get secrets
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")
kite = KiteConnect(api_key=api_key)

# This file will act as a flag for successful login
TOKEN_FILE = "access_token.txt"

def start_redirect_server():
    class TokenHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_path.query)

            try:
                request_token = params.get("request_token")[0]
                data = kite.generate_session(request_token, api_secret=api_secret)
                access_token = data["access_token"]

                # Save to file
                with open(TOKEN_FILE, "w") as f:
                    f.write(access_token)

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("<h2>✅ Login successful. You can close this tab.</h2>")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"<h2>❌ Login failed: {str(e)}</h2>".encode())

    PORT = 8000
    with socketserver.TCPServer(("", PORT), TokenHandler) as httpd:
        httpd.handle_request()


# 🌐 Streamlit UI
st.set_page_config(page_title="Zerodha Login", layout="centered")
st.title("🔐 Zerodha Kite Login")

# Show login status
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    st.success("✅ Zerodha login successful. Token saved.")
    st.code(token)
else:
    if st.button("Login to Zerodha"):
        login_url = kite.login_url()
        threading.Thread(target=start_redirect_server, daemon=True).start()
        st.markdown(
            f'<a href="{login_url}" target="_blank"><button>🔗 Click here to login</button></a>',
            unsafe_allow_html=True
        )
        st.info("Please complete login in new tab. Token will be saved automatically.")
