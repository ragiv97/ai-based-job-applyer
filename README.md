# AI Based Job Applyer

An AI-driven job application bot that discovers relevant job postings, scores them against your profile, tailors a resume per role, and submits applications across multiple platforms (LinkedIn, Naukri, Indeed, Glassdoor, Google Jobs).

## Features

- **Multi-platform discovery** — LinkedIn, Naukri, Indeed, Glassdoor, Google Jobs, Adzuna
- **Relevance scoring & deduplication** — Filters jobs against keywords, experience, and a minimum score
- **Resume tailoring** — Uses Claude to customize your resume per job description, exported as PDF
- **Auto-apply adapters** — Platform-specific Playwright adapters for Easy Apply / Quick Apply flows
- **Question answering** — Handles common application questions from your profile
- **Scheduling** — Runs daily at a configurable time with a per-day application cap
- **Dry-run mode** — Walks the full pipeline without submitting

## Project structure

```
src/
  applicator/    Platform adapters (linkedin, naukri, indeed, greenhouse, lever, workday, ...)
  database/      SQLite models and repository
  discovery/     Scrapers, deduplicator, job scorer
  orchestrator/  Pipeline + scheduler
  resume/        PDF parser, Claude tailor, PDF generator
tests/           Unit tests
main.py          Entry point
config.yaml      Your local config (gitignored)
```

## Setup

1. **Clone and install**
   ```bash
   git clone https://github.com/ragiv97/ai-based-job-applyer.git
   cd ai-based-job-applyer
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure**
   ```bash
   cp config.yaml.example config.yaml
   cp .env.example .env
   ```
   Edit `config.yaml` (keywords, profile, platforms) and `.env` (API keys, platform credentials).

3. **Add your resume**
   Place your base resume at `data/base_resume.pdf`.

4. **Initialize the database**
   ```bash
   python main.py --mode init
   ```

## Usage

| Command | Purpose |
|---|---|
| `python main.py --mode discover` | Scrape and score jobs only |
| `python main.py --mode run` | Run the full pipeline once (discover → score → tailor → apply) |
| `python main.py --mode run --platform linkedin` | Limit applications to a single platform |
| `python main.py --mode run --limit 5` | Cap applications for this run |
| `python main.py --mode schedule` | Run on the daily schedule defined in `config.yaml` |

Set `DRY_RUN=true` in `.env` to stop short of actually submitting applications.

## Required credentials (`.env`)

- `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` — free at developer.adzuna.com
- `MUSE_API_KEY` — The Muse jobs API
- `LINKEDIN_EMAIL`, `LINKEDIN_PASSWORD`
- `NAUKRI_EMAIL`, `NAUKRI_PASSWORD`
- `INDEED_EMAIL`, `INDEED_PASSWORD`
- `GMAIL_EMAIL`, `GMAIL_APP_PASSWORD` — for notifications

## Tests

```bash
pytest
```

## Notes

- `config.yaml`, `.env`, `data/jobs.db`, `data/base_resume.pdf`, `tailored_resumes/`, `logs/`, and `browser_data/` are gitignored.
- Respect each platform's Terms of Service. Use responsibly.
