import yaml
from core.zerodha_api import get_ltp, get_next_week_expiry

with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

def check_and_trigger(action):
    instrument = config['strategy']['instrument']
    offset = config['strategy']['strike_offset']

    ltp = get_ltp(instrument)
    ce_strike = round((ltp + offset) / 50) * 50
    pe_strike = round((ltp - offset) / 50) * 50
    expiry = get_next_week_expiry()

    print(f"\n=== TRIGGER: {action.upper()} ===")
    print(f"{instrument} LTP: {ltp}")
    print(f"Expiry: {expiry}")
    print(f"Buy CE: {ce_strike} | Buy PE: {pe_strike}")
    print("=========================\n")
