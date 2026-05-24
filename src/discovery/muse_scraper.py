import logging
import requests

log = logging.getLogger(__name__)

MUSE_BASE = "https://www.themuse.com/api/public/jobs"


def scrape_muse(keywords: list[str], locations: list[str]) -> list[dict]:
    """Scrape jobs from The Muse API (free, no key required for public endpoint)."""
    all_jobs = []

    for keyword in keywords:
        for location in locations:
            try:
                params = {
                    "category": keyword,
                    "location": location,
                    "page": 1,
                }

                resp = requests.get(MUSE_BASE, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                for result in data.get("results", []):
                    locs = ", ".join(
                        loc.get("name", "") for loc in result.get("locations", [])
                    )
                    job = {
                        "title": result.get("name", ""),
                        "company": result.get("company", {}).get("name", "Unknown"),
                        "location": locs or location,
                        "platform": "the_muse",
                        "job_url": f"https://www.themuse.com/jobs/{result.get('id', '')}",
                        "description": result.get("contents", "")[:5000],
                    }
                    if job["title"] and job["company"]:
                        all_jobs.append(job)

                log.info(f"Muse: {len(data.get('results', []))} jobs for '{keyword}' in '{location}'")

            except Exception as e:
                log.error(f"Muse error for '{keyword}' in '{location}': {e}")

    return all_jobs
