import json
from pathlib import Path
from datetime import datetime

def place_strangle_order(kite, ce_symbol, pe_symbol, quantity):
    orders = []
    for symbol in [ce_symbol, pe_symbol]:
        order_id = kite.place_order(
            tradingsymbol=symbol,
            exchange="NFO",
            transaction_type="BUY",
            quantity=quantity,
            order_type="MARKET",
            product="NRML",
            variety="regular"
        )
        orders.append({"symbol": symbol, "order_id": order_id})
    
    log_orders(orders)
    return orders

def log_orders(order_data):
    log_file = Path("logs/orders_log.json")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    if log_file.exists():
        with open(log_file, "r") as f:
            existing = json.load(f)
    else:
        existing = []

    for entry in order_data:
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing.append(entry)

    with open(log_file, "w") as f:
        json.dump(existing, f, indent=2)
