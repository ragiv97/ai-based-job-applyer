#!/usr/bin/env python3
"""AI Job Application Bot — Main Entry Point"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from src.database.models import init_db


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main():
    load_dotenv()
    setup_logging()
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="AI Job Application Bot")
    parser.add_argument("--mode", choices=["run", "schedule", "discover", "init"],
                        default="run", help="Execution mode")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max applications this run (0 = use config)")
    parser.add_argument("--config", default="config.yaml",
                        help="Path to config file")
    parser.add_argument("--platform", default=None,
                        help="Filter applications to a single platform (e.g. linkedin)")
    args = parser.parse_args()

    # Force dry run if env set
    if os.getenv("DRY_RUN", "false").lower() == "true":
        log.info("*** DRY RUN MODE ENABLED ***")

    if args.mode == "init":
        init_db()
        log.info("Database initialized. Place your resume at data/base_resume.pdf")
        log.info("Edit config.yaml and .env with your details, then run: python main.py --mode run")
        return

    if args.mode == "discover":
        init_db()
        from src.orchestrator.pipeline import discover_jobs, score_and_filter, load_config
        config = load_config(args.config)
        new_jobs = discover_jobs(config)
        log.info(f"Discovered {len(new_jobs)} new jobs")
        matched = score_and_filter(config)
        log.info(f"{len(matched)} QA jobs matched (score >= {config['job_search'].get('min_relevance_score', 6)}) and are ready in the DB")
        return

    if args.mode == "schedule":
        init_db()
        from src.orchestrator.scheduler import start_scheduler
        start_scheduler(args.config)
        return

    # Default: run pipeline once
    init_db()
    from src.orchestrator.pipeline import run_daily_pipeline
    run_daily_pipeline(config_path=args.config, limit=args.limit, platform=args.platform)


if __name__ == "__main__":
    main()
