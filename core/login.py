from kiteconnect import KiteConnect
import os
import webbrowser
import http.server
import socketserver
import urllib.parse
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
os.makedirs("tokens", exist_ok=True)

def get_secret(key):
    try:
        # Try Streamlit secrets (Cloud)
        return st.secrets[key]
    except Exception:
        # Fallback to local .env or YAML config
        return os.getenv(key)

api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")

kite = KiteConnect(api_key=api_key)
login_url = kite.login_url()
print(f"Open the following URL in your browser:\n{login_url}")
webbrowser.open(login_url)

class TokenHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        request_token = params.get("request_token")[0]

        print(f"Received request_token: {request_token}")
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        print(f"Access Token: {access_token}")

        # Update .env file
        with open(".env", "r") as f:
            lines = f.readlines()

        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("ZERODHA_ACCESS_TOKEN="):
                    f.write(f"ZERODHA_ACCESS_TOKEN={access_token}\n")
                else:
                    f.write(line)

        print("✅ Access token saved to .env")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Login Successful. You can close this tab now.</h2>")

PORT = 8000
with socketserver.TCPServer(("", PORT), TokenHandler) as httpd:
    print("Listening on port 8000 for redirect...")
    httpd.handle_request()
