import logging
from jobspy import scrape_jobs

log = logging.getLogger(__name__)


COUNTRY_LOCATION = {
    "India": "India",
    "USA": "United States",
    "UK": "United Kingdom",
    "Canada": "Canada",
    "Australia": "Australia",
}


def scrape_jobspy(keywords: list[str], locations: list[str], platforms: dict,
                  countries: list[str] | None = None) -> list[dict]:
    """Scrape remote jobs from multiple platforms using python-jobspy across countries."""
    all_jobs = []

    site_names = []
    if platforms.get("linkedin"):
        site_names.append("linkedin")
    if platforms.get("indeed"):
        site_names.append("indeed")
    if platforms.get("glassdoor"):
        site_names.append("glassdoor")
    if platforms.get("google_jobs"):
        site_names.append("google")
    if platforms.get("ziprecruiter"):
        site_names.append("zip_recruiter")

    if not site_names:
        log.warning("No platforms enabled for JobSpy")
        return []

    countries = countries or ["India"]

    for country in countries:
        country_loc = COUNTRY_LOCATION.get(country, country)
        for keyword in keywords:
            try:
                log.info(f"Scraping: '{keyword}' remote in '{country}' on {site_names}")
                df = scrape_jobs(
                    site_name=site_names,
                    search_term=keyword,
                    location=country_loc,
                    is_remote=True,
                    results_wanted=100,
                    hours_old=168,
                    country_indeed=country,
                )

                if df is None or df.empty:
                    log.info(f"No results for '{keyword}' in '{country}'")
                    continue

                for _, row in df.iterrows():
                    job = {
                        "title": str(row.get("title", "")),
                        "company": str(row.get("company_name", row.get("company", ""))),
                        "location": str(row.get("location", "")),
                        "platform": str(row.get("site", "")),
                        "job_url": str(row.get("job_url", "")),
                        "description": str(row.get("description", ""))[:5000],
                    }
                    if job["title"] and job["company"]:
                        all_jobs.append(job)

                log.info(f"Found {len(df)} jobs for '{keyword}' in '{country}'")

            except Exception as e:
                log.error(f"JobSpy error for '{keyword}' in '{country}': {e}")

    return all_jobs
