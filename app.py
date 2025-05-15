from core.scheduler import schedule_jobs
from core.strategy import check_and_trigger
import yaml
import os

def check_token():
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
    if not config["zerodha"].get("access_token"):
        print("⚠️ No access token found. Run: python core/login.py")
        exit()

if __name__ == "__main__":
    check_token()
    schedule_jobs()

check_and_trigger("entry")
