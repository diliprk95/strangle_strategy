# core/strategy_runner.py

import datetime
from core.logger import log_event
from core.zerodha_api import get_kite_client, get_ltp, get_next_week_expiry
from core.config_handler import load_config


def should_trigger_entry(now, config):
    entry_day = config["strategy"]["entry_day"]
    entry_time = config["strategy"]["entry_time"]
    entry_dt = datetime.datetime.strptime(entry_time, "%H:%M").time()
    return now.strftime("%A") == entry_day and now.time().hour == entry_dt.hour and now.time().minute == entry_dt.minute


def should_trigger_exit(now, config):
    exit_day = config["strategy"]["exit_day"]
    exit_time = config["strategy"]["exit_time"]
    exit_dt = datetime.datetime.strptime(exit_time, "%H:%M").time()
    return now.strftime("%A") == exit_day and now.time().hour == exit_dt.hour and now.time().minute == exit_dt.minute


def place_order(kite, symbol, quantity):
    return kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=kite.EXCHANGE_NFO,
        tradingsymbol=symbol,
        transaction_type=kite.TRANSACTION_TYPE_BUY,
        quantity=quantity,
        order_type=kite.ORDER_TYPE_MARKET,
        product=kite.PRODUCT_MIS
    )


def run_strategy():
    config = load_config()
    strategy = config["strategy"]

    symbol = strategy.get("symbol", "NIFTY")
    strike_distance = strategy.get("strike_distance", 300)
    quantity = strategy.get("quantity", 50)
    order_enabled = strategy.get("order_enabled", False)
    round_base = strategy.get("round_base", 50)

    entry_day = strategy.get("entry_day", "Friday")
    entry_time = strategy.get("entry_time", "10:30")
    exit_day = strategy.get("exit_day", "Monday")
    exit_time = strategy.get("exit_time", "15:00")

    now = datetime.datetime.now()
    today = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    kite = get_kite_client()
    expiry = get_next_week_expiry()

    try:
        ltp = get_ltp(symbol)
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Error fetching LTP: {e}",
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    rounded_price = round(ltp / round_base) * round_base
    ce_strike = rounded_price + strike_distance
    pe_strike = rounded_price - strike_distance

    ce_symbol = f"{symbol}{expiry}C{ce_strike}"
    pe_symbol = f"{symbol}{expiry}P{pe_strike}"

    if today == entry_day and current_time == entry_time:
        if order_enabled:
            try:
                ce_order_id = place_order(kite, ce_symbol, quantity)
                pe_order_id = place_order(kite, pe_symbol, quantity)

                result = {
                    "status": "ENTRY",
                    "message": "✅ Orders placed",
                    "buy_ce": ce_symbol,
                    "buy_pe": pe_symbol,
                    "ce_order_id": ce_order_id,
                    "pe_order_id": pe_order_id,
                    "ltp": ltp,
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
                }
                log_event(result)
            except Exception as e:
                result = {
                    "status": "ERROR",
                    "message": f"❌ Order placement failed: {e}",
                    "buy_ce": ce_symbol,
                    "buy_pe": pe_symbol,
                    "ltp": ltp,
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
                }
                log_event(result)
        else:
            result = {
                "status": "ENTRY",
                "message": "Entry time matched but order_enabled is False",
                "buy_ce": ce_symbol,
                "buy_pe": pe_symbol,
                "ltp": ltp,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
            }
            log_event(result)

    elif today == exit_day and current_time == exit_time:
        result = {
            "status": "EXIT",
            "message": "Exit time reached. You can close your positions.",
            "buy_ce": ce_symbol,
            "buy_pe": pe_symbol,
            "ltp": ltp,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        log_event(result)

    else:
        result = {
            "status": "WAIT",
            "message": f"Waiting for strategy time window. Current: {today} {current_time}",
            "buy_ce": ce_symbol,
            "buy_pe": pe_symbol,
            "ltp": ltp,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        log_event(result)

    return result
