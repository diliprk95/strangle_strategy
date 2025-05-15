# core/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from core.config_handler import load_config
from core.strategy_runner import run_strategy
import logging

logging.basicConfig(level=logging.INFO)
scheduler = BackgroundScheduler()
job = None

def schedule_jobs():
    config = load_config()
    strategy = config.get("strategy", {})

    entry_day = strategy["entry_day"]
    entry_time = strategy["entry_time"]
    exit_day = strategy["exit_day"]
    exit_time = strategy["exit_time"]

    def match_day_time(day_str, time_str):
        # APScheduler requires 24hr format
        hour, minute = map(int, time_str.split(":"))
        return {"day_of_week": day_str.lower(), "hour": hour, "minute": minute}

    # Entry Job
    scheduler.add_job(
        lambda: run_strategy("entry"),
        trigger="cron",
        **match_day_time(entry_day, entry_time),
        id="entry_job",
        replace_existing=True
    )

    # Exit Job
    scheduler.add_job(
        lambda: run_strategy("exit"),
        trigger="cron",
        **match_day_time(exit_day, exit_time),
        id="exit_job",
        replace_existing=True
    )

def start_scheduler(interval_minutes=1):
    global job
    if not scheduler.running:
        scheduler.start()
    if job:
        job.remove()
    job = scheduler.add_job(run_strategy, 'interval', minutes=interval_minutes, id="strategy_job")
    print(f"[{datetime.now()}] Scheduler started with interval: {interval_minutes} minute(s)")

def stop_scheduler():
    global job
    if job:
        job.remove()
        job = None
        print(f"[{datetime.now()}] Scheduler stopped")

def is_scheduler_running():
    return scheduler.running and job is not None