import json
import logging
import re
import subprocess
import time
from ..database.repository import JobRepository

log = logging.getLogger(__name__)

# Keywords that strongly indicate a relevant QA/Automation role
STRONG_MATCH_KEYWORDS = [
    "qa automation", "qa engineer", "quality assurance", "test automation",
    "sdet", "selenium", "playwright", "pytest", "python qa",
    "automation engineer", "automation testing", "test engineer",
    "software test", "api testing", "ci/cd", "jenkins",
]

# Keywords that boost score
BOOST_KEYWORDS = [
    "python", "java", "javascript", "rest api", "postman",
    "jira", "agile", "scrum", "git", "docker", "aws",
    "regression", "functional testing", "performance testing",
    "cypress", "appium", "robot framework", "cucumber",
]

# Keywords that reduce score (not relevant)
NEGATIVE_KEYWORDS = [
    "mechanical", "electrical", "civil", "chemical",
    "hardware", "plc", "scada", "hvac", "manufacturing",
    "sales", "marketing", "accounting", "hr ", "recruiter",
]


def score_job_local(job: dict, config_keywords: list[str]) -> int:
    """Score job relevance using keyword matching. Fast, no API calls."""
    title = (job.get("title") or "").lower()
    description = (job.get("description") or "").lower()
    text = f"{title} {description}"

    score = 4  # Base score

    # Strong match on title
    for kw in STRONG_MATCH_KEYWORDS:
        if kw in title:
            score += 3
            break

    # Strong match in description
    strong_in_desc = sum(1 for kw in STRONG_MATCH_KEYWORDS if kw in description)
    score += min(strong_in_desc, 2)  # Up to +2

    # Boost keywords
    boost_count = sum(1 for kw in BOOST_KEYWORDS if kw in text)
    score += min(boost_count // 2, 2)  # Up to +2

    # Config keyword match in title
    for kw in config_keywords:
        if kw.lower() in title:
            score += 1
            break

    # Negative keywords penalty
    for kw in NEGATIVE_KEYWORDS:
        if kw in title:
            score -= 3
            break

    return max(1, min(10, score))


def score_job_claude(job: dict, profile_summary: str) -> int:
    """Fallback: Use Claude Code CLI to score job relevance 1-10."""
    prompt = f"""You are a job relevance scorer. Rate how well this job matches the candidate profile.

CANDIDATE PROFILE: {profile_summary}
JOB TITLE: {job['title']}
COMPANY: {job['company']}
JOB DESCRIPTION: {(job.get('description') or '')[:500]}

Return ONLY a JSON: {{"score": 7, "reason": "Good match for Python skills"}}
Score 1-10. 10 = perfect match. Below 6 = reject."""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout.strip()

        if "rate limit" in output.lower() or "error" in output.lower():
            return -1  # Signal to use local scorer

        start = output.find("{")
        end = output.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(output[start:end])
            score = int(data.get("score", 0))
            reason = data.get("reason", "")
            log.info(f"Claude score {score}/10 for '{job['title']}': {reason}")
            return max(1, min(10, score))

        return -1
    except Exception:
        return -1


def score_all_unscored(profile_summary: str, min_score: int = 6, config_keywords: list[str] = None):
    """Score all unscored jobs. Uses fast local scoring, with optional Claude fallback."""
    repo = JobRepository()
    unscored = repo.get_unscored_jobs()
    keywords = config_keywords or []

    log.info(f"Scoring {len(unscored)} unscored jobs (keyword-based)")

    for job in unscored:
        score = score_job_local(job, keywords)
        log.info(f"Score {score}/10 for '{job['title']}' at {job['company']}")

        repo.update_score(job["id"], score)

        if score < min_score:
            repo.update_status(job["id"], "SKIPPED")

    scored_above = sum(1 for j in unscored if score_job_local(j, keywords) >= min_score)
    log.info(f"Scoring complete: {scored_above} jobs scored >= {min_score}, {len(unscored) - scored_above} skipped")
