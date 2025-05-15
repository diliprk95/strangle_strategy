import os
import yaml
import streamlit as st
from kiteconnect import KiteConnect
from datetime import date, timedelta

CONFIG_PATH = os.path.join("config", "settings.yaml")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

config = load_config()

def get_secret(key):
    try:
        # Try Streamlit secrets (Cloud)
        return st.secrets[key]
    except Exception:
        # Fallback to local .env or YAML config
        return os.getenv(key)

api_key = get_secret("ZERODHA_API_KEY")
api_secret = get_secret("ZERODHA_API_SECRET")
access_token_path = get_secret("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)

def is_token_valid():
    if not os.path.exists(access_token_path):
        return False
    with open(access_token_path, "r") as f:
        token = f.read().strip()
    try:
        kite.set_access_token(token)
        kite.profile()  # Test token by calling profile
        return True
    except Exception:
        return False

def get_login_url():
    return kite.login_url()

def generate_access_token(request_token: str):
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    with open(access_token_path, "w") as f:
        f.write(access_token)
    kite.set_access_token(access_token)
    return access_token

def get_kite_client():
    return kite

def get_ltp(symbol: str):
    full_symbol = f"NSE:{symbol} 50"
    ltp_data = kite.ltp([full_symbol])
    return ltp_data[full_symbol]["last_price"]

def get_next_week_expiry():
    today = date.today()
    days_ahead = 3 - today.weekday()  # Thursday = 3
    if days_ahead <= 0:
        days_ahead += 7
    next_thursday = today + timedelta(days=days_ahead + 7)
    return next_thursday.strftime("%d-%b-%Y")
