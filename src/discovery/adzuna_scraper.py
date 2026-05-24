import logging
import os
import requests

log = logging.getLogger(__name__)

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"


def scrape_adzuna(keywords: list[str], locations: list[str], country: str = "in") -> list[dict]:
    """Scrape jobs from Adzuna API (free tier)."""
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        log.info("Adzuna API credentials not configured, skipping")
        return []

    all_jobs = []

    for keyword in keywords:
        for location in locations:
            try:
                url = f"{ADZUNA_BASE}/{country}/search/1"
                params = {
                    "app_id": app_id,
                    "app_key": app_key,
                    "what": keyword,
                    "where": location,
                    "results_per_page": 25,
                    "max_days_old": 1,
                    "content-type": "application/json",
                }

                resp = requests.get(url, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                for result in data.get("results", []):
                    job = {
                        "title": result.get("title", ""),
                        "company": result.get("company", {}).get("display_name", "Unknown"),
                        "location": result.get("location", {}).get("display_name", ""),
                        "platform": "adzuna",
                        "job_url": result.get("redirect_url", ""),
                        "description": result.get("description", "")[:5000],
                    }
                    if job["title"] and job["company"]:
                        all_jobs.append(job)

                log.info(f"Adzuna: {len(data.get('results', []))} jobs for '{keyword}' in '{location}'")

            except Exception as e:
                log.error(f"Adzuna error for '{keyword}' in '{location}': {e}")

    return all_jobs
