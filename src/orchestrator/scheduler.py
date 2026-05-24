import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from .pipeline import run_daily_pipeline, load_config

log = logging.getLogger(__name__)


def start_scheduler(config_path: str = "config.yaml"):
    """Start the APScheduler to run the pipeline daily."""
    config = load_config(config_path)
    schedule = config.get("schedule", {})

    run_time = schedule.get("run_time", "08:00")
    timezone = schedule.get("timezone", "Asia/Kolkata")
    hour, minute = run_time.split(":")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_daily_pipeline,
        trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=timezone),
        id="daily_pipeline",
        name="Daily Job Application Pipeline",
        kwargs={"config_path": config_path},
        misfire_grace_time=3600,
    )

    log.info(f"Scheduler configured: daily at {run_time} ({timezone})")
    log.info("Press Ctrl+C to exit")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped")
