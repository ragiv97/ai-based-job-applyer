import hashlib
import json
import logging
import os
from datetime import datetime
from ..database.repository import JobRepository

log = logging.getLogger(__name__)

JOBS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "jobs.json")


def compute_hash(job: dict) -> str:
    key = f"{job['title'].lower().strip()}|{job['company'].lower().strip()}|{job.get('location', '').lower().strip()}"
    return hashlib.sha256(key.encode()).hexdigest()


def save_jobs_to_json(new_jobs: list[dict]):
    """Append new jobs to a local JSON file."""
    existing = []
    if os.path.exists(JOBS_JSON_PATH):
        with open(JOBS_JSON_PATH, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    for job in new_jobs:
        existing.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "platform": job.get("platform", ""),
            "job_url": job.get("job_url", ""),
            "description": job.get("description", "")[:500],
            "hash": job.get("hash", ""),
            "discovered_at": datetime.now().isoformat(),
        })

    with open(JOBS_JSON_PATH, "w") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    log.info(f"Saved {len(existing)} total jobs to {JOBS_JSON_PATH}")


REMOTE_TOKENS = (
    "remote", "work from home", "work-from-home", "wfh",
    "100% remote", "fully remote", "remote-first",
    "anywhere", "home based", "home-based", "telecommute",
)


def is_remote_job(job: dict) -> bool:
    haystack = " ".join([
        job.get("title", ""),
        job.get("location", ""),
        job.get("description", ""),
    ]).lower()
    return any(tok in haystack for tok in REMOTE_TOKENS)


def deduplicate_and_store(jobs: list[dict]) -> list[dict]:
    """Deduplicate jobs and store new ones in the database + JSON. Returns newly inserted jobs."""
    repo = JobRepository()
    new_jobs = []
    dropped_non_remote = 0

    for job in jobs:
        if not is_remote_job(job):
            dropped_non_remote += 1
            continue
        job["hash"] = compute_hash(job)
        if not repo.job_exists(job["hash"]):
            if repo.insert_job(job):
                new_jobs.append(job)

    log.info(f"Remote filter: dropped {dropped_non_remote} non-remote jobs")
    log.info(f"Deduplication: {len(jobs) - dropped_non_remote} remote jobs → {len(new_jobs)} new jobs stored")

    if new_jobs:
        save_jobs_to_json(new_jobs)

    return new_jobs
