import os
import json
from datetime import datetime

LOG_FILE = "logs/strategy_log.json"

def log_event(event: dict):
    with open(LOG_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {event['status']} - {event.get('message', '')}\n")
        if event["status"] == "ENTRY":
            f.write(f"  CE: {event['buy_ce']} | PE: {event['buy_pe']}\n")
            if "order_id_ce" in event:
                f.write(f"  Order IDs => CE: {event['order_id_ce']}, PE: {event['order_id_pe']}\n")
        f.write("\n")

def log_event(event_data):
    os.makedirs("logs", exist_ok=True)
    
    # Add timestamp if not already added
    if "timestamp" not in event_data:
        event_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    
    logs.insert(0, event_data)  # newest first

    with open(LOG_FILE, "w") as f:
        json.dump(logs[:100], f, indent=2)  # Keep only latest 100 logs

