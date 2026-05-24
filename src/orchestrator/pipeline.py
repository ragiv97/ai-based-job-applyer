import logging
import os
import random
import time

import yaml
from dotenv import load_dotenv

from ..database.models import init_db
from ..database.repository import JobRepository
from ..discovery.jobspy_scraper import scrape_jobspy
from ..discovery.adzuna_scraper import scrape_adzuna
from ..discovery.muse_scraper import scrape_muse
from ..discovery.deduplicator import deduplicate_and_store
from ..discovery.job_scorer import score_all_unscored
from ..resume.pdf_parser import parse_resume_pdf
from ..resume.claude_tailor import tailor_resume
from ..resume.pdf_generator import generate_pdf
from ..applicator.base_adapter import detect_platform
from ..applicator.linkedin_adapter import LinkedInAdapter
from ..applicator.naukri_adapter import NaukriAdapter
from ..applicator.indeed_adapter import IndeedAdapter
from ..applicator.greenhouse_adapter import GreenhouseAdapter
from ..applicator.lever_adapter import LeverAdapter
from ..applicator.workday_adapter import WorkdayAdapter
from ..applicator.generic_adapter import GenericAdapter
from ..notification.email_sender import send_application_email, send_daily_summary

log = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_adapter(platform: str, dry_run: bool = False):
    adapters = {
        "linkedin": LinkedInAdapter,
        "naukri": NaukriAdapter,
        "indeed": IndeedAdapter,
        "greenhouse": GreenhouseAdapter,
        "lever": LeverAdapter,
        "workday": WorkdayAdapter,
    }
    adapter_cls = adapters.get(platform, GenericAdapter)
    return adapter_cls(dry_run=dry_run)


def discover_jobs(config: dict) -> list[dict]:
    """Phase 1: Discover jobs from all enabled platforms."""
    keywords = config["job_search"]["keywords"]
    locations = config["job_search"]["locations"]
    platforms = config.get("platforms", {})

    all_jobs = []

    countries = config["job_search"].get("countries")

    # JobSpy (LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter)
    jobspy_jobs = scrape_jobspy(keywords, locations, platforms, countries=countries)
    all_jobs.extend(jobspy_jobs)

    # Adzuna API
    adzuna_jobs = scrape_adzuna(keywords, locations)
    all_jobs.extend(adzuna_jobs)

    # The Muse API
    muse_jobs = scrape_muse(keywords, locations)
    all_jobs.extend(muse_jobs)

    log.info(f"Total raw jobs discovered: {len(all_jobs)}")

    # Deduplicate and store
    new_jobs = deduplicate_and_store(all_jobs)
    return new_jobs


def score_and_filter(config: dict) -> list[dict]:
    """Phase 2: Score unscored jobs and return those above threshold."""
    profile = config.get("applicant_profile", {})
    profile_summary = (
        f"Name: {profile.get('name', '')}. "
        f"Experience: {config['job_search'].get('experience_years', 0)} years. "
        f"Keywords: {', '.join(config['job_search']['keywords'])}. "
        f"Locations: {', '.join(config['job_search']['locations'])}."
    )

    min_score = config["job_search"].get("min_relevance_score", 6)
    keywords = config["job_search"].get("keywords", [])
    score_all_unscored(profile_summary, min_score, config_keywords=keywords)

    repo = JobRepository()
    return repo.get_ready_to_apply(min_score, config["job_search"].get("max_applications_per_day", 20))


def apply_to_job(job: dict, resume_pdf_path: str, config: dict, browser_context) -> bool:
    """Phase 4: Apply to a single job using the appropriate adapter."""
    platform = detect_platform(job.get("job_url", ""))
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    adapter = get_adapter(platform, dry_run=dry_run)

    # Check blacklist
    blacklist = [c.lower() for c in config["job_search"].get("blacklisted_companies", [])]
    if job.get("company", "").lower() in blacklist:
        log.info(f"Skipping blacklisted company: {job['company']}")
        return False

    page = browser_context.new_page()
    try:
        success = adapter.apply(page, job, resume_pdf_path, config.get("applicant_profile", {}))
        return success
    finally:
        page.close()


def run_daily_pipeline(config_path: str = "config.yaml", limit: int = 0, platform: str | None = None):
    """Main pipeline controller - runs all phases."""
    load_dotenv()
    config = load_config(config_path)
    init_db()

    repo = JobRepository()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    log.info("=== Daily Job Bot Pipeline Starting ===")
    if dry_run:
        log.info("*** DRY RUN MODE — will NOT submit applications ***")

    # Phase 1: Discover new jobs
    new_jobs = discover_jobs(config)
    log.info(f"Discovered {len(new_jobs)} new jobs")

    # Phase 2: Score and filter
    scored_jobs = score_and_filter(config)
    log.info(f"{len(scored_jobs)} jobs passed relevance filter")

    max_apps = limit or config["job_search"].get("max_applications_per_day", 20)
    daily_applied = repo.get_daily_applied_count()
    remaining = max(0, max_apps - daily_applied)

    if remaining == 0:
        log.info("Daily application limit reached")
        return

    if platform:
        scored_jobs = [j for j in scored_jobs if detect_platform(j.get("job_url", "")) == platform]
        log.info(f"Platform filter '{platform}': {len(scored_jobs)} jobs remain")
    jobs_to_apply = scored_jobs[:remaining]

    # Parse base resume once
    base_resume_path = os.path.join("data", "base_resume.pdf")
    if not os.path.exists(base_resume_path):
        log.error(f"Base resume not found at {base_resume_path}")
        return

    resume_markdown = parse_resume_pdf(base_resume_path)

    # Set up browser
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    applied = 0
    failed = 0
    skipped = len(new_jobs) - len(scored_jobs)

    with sync_playwright() as p:
        browser_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "browser_data")
        os.makedirs(browser_data_dir, exist_ok=True)

        context = p.chromium.launch_persistent_context(
            browser_data_dir,
            channel="chrome",
            headless=False,
            viewport={"width": 1280, "height": 800},
        )

        # Apply stealth to all pages
        stealth = Stealth()
        for page in context.pages:
            stealth.apply_stealth_sync(page)

        context.on("page", lambda page: stealth.apply_stealth_sync(page))

        # Login to platforms that need it
        logged_in = set()
        for job in jobs_to_apply:
            platform = detect_platform(job.get("job_url", ""))
            if platform not in logged_in and platform in ("linkedin", "naukri", "indeed"):
                adapter = get_adapter(platform, dry_run=dry_run)
                if adapter.login(context):
                    logged_in.add(platform)

        # Apply to each job
        for job in jobs_to_apply:
            try:
                repo.update_status(job["id"], "TAILORING")

                # Phase 3: Tailor resume
                resume_data = tailor_resume(resume_markdown, job)
                tailored_pdf = generate_pdf(resume_data, job)
                repo.update_status(job["id"], "APPLYING", tailored_resume_path=tailored_pdf)

                # Phase 4: Apply
                success = apply_to_job(job, tailored_pdf, config, context)

                if success:
                    repo.update_status(job["id"], "APPLIED", tailored_resume_path=tailored_pdf)
                    send_application_email(job, tailored_pdf)
                    applied += 1
                    log.info(f"Successfully applied to '{job['title']}' at {job['company']}")

                    # Human-like delay between applications
                    delay = random.randint(45, 90)
                    log.info(f"Waiting {delay}s before next application...")
                    time.sleep(delay)
                else:
                    repo.update_status(job["id"], "FAILED")
                    failed += 1

            except Exception as e:
                log.error(f"Failed to apply to {job['title']} at {job['company']}: {e}")
                repo.update_status(job["id"], "FAILED")
                failed += 1

        context.close()

    # Phase 5: Daily summary
    send_daily_summary(applied, failed, skipped, len(new_jobs))
    log.info(f"=== Pipeline Complete. Applied: {applied}, Failed: {failed}, Skipped: {skipped} ===")
