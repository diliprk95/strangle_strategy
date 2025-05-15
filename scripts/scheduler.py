import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apscheduler.schedulers.blocking import BlockingScheduler
from core.strategy_runner import run_strategy
from core.config_handler import load_config

def scheduled_task():
    config = load_config()
    if config.get("strategy", {}).get("order_enabled"):
        run_strategy(mode="schedule")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_task, "cron", day_of_week="mon-fri", minute="*/1")
    print("Scheduler started... Ctrl+C to stop.")
    scheduler.start()
