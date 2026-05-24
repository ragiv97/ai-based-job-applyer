import json
import logging
import re
import subprocess

log = logging.getLogger(__name__)


def parse_resume_markdown(md: str) -> dict:
    """Parse resume markdown into structured JSON for PDF generation."""
    lines = md.strip().split("\n")
    data = {
        "name": "",
        "contact": {"email": "", "phone": "", "linkedin": ""},
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
    }

    # Extract name (usually first non-empty line or first heading)
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            data["name"] = line.strip("*# ")
            break
        elif line.startswith("#"):
            data["name"] = line.lstrip("# ").strip()
            break

    # Extract contact info
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', md)
    if email_match:
        data["contact"]["email"] = email_match.group()

    phone_match = re.search(r'[\+]?[\d\s\-()]{10,}', md)
    if phone_match:
        data["contact"]["phone"] = phone_match.group().strip()

    linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[\w-]+/?', md)
    if linkedin_match:
        data["contact"]["linkedin"] = linkedin_match.group()

    # Extract sections by headings
    sections = {}
    current_section = ""
    current_content = []

    for line in lines:
        if line.startswith("#"):
            if current_section:
                sections[current_section.lower()] = "\n".join(current_content)
            current_section = line.lstrip("# ").strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section.lower()] = "\n".join(current_content)

    # Parse summary
    for key in ["summary", "objective", "about", "profile"]:
        if key in sections:
            data["summary"] = sections[key].strip()
            break

    # Parse experience
    for key in sections:
        if "experience" in key or "work" in key or "employment" in key:
            data["experience"] = parse_experience_section(sections[key])
            break

    # Parse education
    for key in sections:
        if "education" in key:
            data["education"] = parse_education_section(sections[key])
            break

    # Parse skills
    for key in sections:
        if "skill" in key or "technical" in key:
            text = sections[key]
            skills = re.split(r'[,\n•\-|]', text)
            data["skills"] = [s.strip().strip("*").strip() for s in skills if s.strip() and len(s.strip()) > 1]
            break

    # Parse projects
    for key in sections:
        if "project" in key:
            data["projects"] = parse_projects_section(sections[key])
            break

    return data


def parse_experience_section(text: str) -> list[dict]:
    """Parse experience section into structured list."""
    experiences = []
    current = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect new job entry (bold text or line with company indicators)
        if line.startswith("**") or (line.startswith("*") and not line.startswith("* ")) or re.match(r'^[A-Z].*\|', line):
            if current:
                experiences.append(current)
            parts = line.strip("*").strip()
            # Try to split title | company | duration
            segments = re.split(r'\s*[\|–—-]\s*', parts)
            current = {
                "title": segments[0].strip() if segments else parts,
                "company": segments[1].strip() if len(segments) > 1 else "",
                "duration": segments[-1].strip() if len(segments) > 2 else "",
                "bullets": [],
            }
        elif line.startswith(("- ", "* ", "• ")) and current:
            bullet = line.lstrip("-*• ").strip()
            if bullet:
                current["bullets"].append(bullet)
        elif current and not current.get("company") and line:
            current["company"] = line.strip("*").strip()

    if current:
        experiences.append(current)

    return experiences


def parse_education_section(text: str) -> list[dict]:
    """Parse education section."""
    entries = []
    for line in text.split("\n"):
        line = line.strip().strip("*-• ")
        if not line:
            continue
        segments = re.split(r'\s*[\|–—,-]\s*', line)
        entry = {
            "degree": segments[0].strip() if segments else line,
            "institution": segments[1].strip() if len(segments) > 1 else "",
            "year": segments[-1].strip() if len(segments) > 2 else "",
        }
        if entry["degree"]:
            entries.append(entry)
    return entries


def parse_projects_section(text: str) -> list[dict]:
    """Parse projects section."""
    projects = []
    current = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith(("**", "###")):
            if current:
                projects.append(current)
            current = {"name": line.strip("*# "), "description": "", "tech": ""}
        elif line.startswith(("- ", "* ", "• ")) and current:
            desc = line.lstrip("-*• ").strip()
            if "tech" in desc.lower() or "stack" in desc.lower():
                current["tech"] = desc
            else:
                current["description"] += (" " + desc if current["description"] else desc)
        elif current:
            current["description"] += (" " + line if current["description"] else line)

    if current:
        projects.append(current)
    return projects


def tailor_summary(base_summary: str, job: dict) -> str:
    """Generate a tailored summary by incorporating job-relevant keywords."""
    title = job.get("title", "")
    company = job.get("company", "")
    desc = (job.get("description") or "").lower()

    # Extract key terms from job description
    qa_terms = []
    term_map = {
        "selenium": "Selenium", "playwright": "Playwright", "cypress": "Cypress",
        "python": "Python", "java": "Java", "javascript": "JavaScript",
        "api testing": "API testing", "rest api": "REST API",
        "ci/cd": "CI/CD", "jenkins": "Jenkins", "docker": "Docker",
        "agile": "Agile", "scrum": "Scrum", "jira": "JIRA",
        "automation": "automation", "manual testing": "manual testing",
        "regression": "regression testing", "performance": "performance testing",
        "aws": "AWS", "azure": "Azure", "kubernetes": "Kubernetes",
    }

    for key, display in term_map.items():
        if key in desc:
            qa_terms.append(display)

    matched = ", ".join(qa_terms[:5]) if qa_terms else "test automation and quality assurance"

    if base_summary:
        return f"{base_summary.rstrip('.')}. Seeking to leverage expertise in {matched} as {title} at {company}."
    else:
        return f"Experienced QA professional with strong skills in {matched}, seeking the {title} role at {company}."


def tailor_resume(resume_markdown: str, job: dict) -> dict:
    """Tailor resume for a specific job. Parses markdown and adjusts content.
    Falls back to Claude CLI if available, otherwise uses local tailoring."""

    # Try Claude CLI first
    try:
        result = _tailor_with_claude(resume_markdown, job)
        if result:
            return result
    except Exception as e:
        log.info(f"Claude CLI unavailable for tailoring, using local method: {e}")

    # Local tailoring
    log.info(f"Tailoring resume locally for '{job['title']}' at {job['company']}")
    data = parse_resume_markdown(resume_markdown)

    # Tailor the summary
    data["summary"] = tailor_summary(data.get("summary", ""), job)

    # Reorder skills to prioritize job-relevant ones
    desc_lower = (job.get("description") or "").lower()
    if data["skills"]:
        relevant = [s for s in data["skills"] if s.lower() in desc_lower]
        others = [s for s in data["skills"] if s.lower() not in desc_lower]
        data["skills"] = relevant + others

    log.info(f"Tailored resume locally for '{job['title']}' at {job['company']}'")
    return data


def _tailor_with_claude(resume_markdown: str, job: dict) -> dict | None:
    """Try Claude CLI for tailoring. Returns None if rate limited."""
    prompt = f"""You are an expert resume writer. Tailor this resume for the job below.

RULES (STRICT):
1. NEVER add skills, experience, or achievements not in the original
2. DO reorder bullet points to emphasize relevant experience first
3. DO mirror keywords from the job description naturally
4. DO rewrite the summary/objective section for this specific role
5. Keep truthful and professional

ORIGINAL RESUME (Markdown):
{resume_markdown}

JOB TITLE: {job['title']}
COMPANY: {job['company']}
JOB DESCRIPTION:
{(job.get('description') or '')[:2000]}

Return ONLY valid JSON matching this schema:
{{
  "name": "...",
  "contact": {{"email": "...", "phone": "...", "linkedin": "..."}},
  "summary": "...",
  "experience": [
    {{
      "title": "...", "company": "...", "duration": "...",
      "bullets": ["...", "..."]
    }}
  ],
  "education": [{{"degree": "...", "institution": "...", "year": "..."}}],
  "skills": ["...", "..."],
  "projects": [{{"name": "...", "description": "...", "tech": "..."}}]
}}"""

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = result.stdout.strip()

    if "rate limit" in output.lower() or "error" in output.lower():
        return None

    start = output.find("{")
    end = output.rfind("}") + 1
    if start >= 0 and end > start:
        data = json.loads(output[start:end])
        log.info(f"Tailored resume via Claude for '{job['title']}' at {job['company']}")
        return data

    return None
