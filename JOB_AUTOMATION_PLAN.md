# 🤖 AI Job Application Automation System
### Complete Project Plan — Powered by Claude Code (Zero Cost)

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [System Architecture](#3-system-architecture)
4. [Project Structure](#4-project-structure)
5. [Phase 1 — Foundation Setup](#phase-1--foundation-setup)
6. [Phase 2 — Job Discovery](#phase-2--job-discovery)
7. [Phase 3 — AI Resume Tailoring](#phase-3--ai-resume-tailoring)
8. [Phase 4 — Browser Automation](#phase-4--browser-automation)
9. [Phase 5 — Email Notifications](#phase-5--email-notifications)
10. [Phase 6 — Orchestration & Scheduling](#phase-6--orchestration--scheduling)
11. [Phase 7 — Anti-Detection & Safety](#phase-7--anti-detection--safety)
12. [Phase 8 — Testing & Launch](#phase-8--testing--launch)
13. [Platform Coverage](#platform-coverage)
14. [Daily Limits & Rates](#daily-limits--rates)
15. [Risk & Mitigation](#risk--mitigation)

---

## 1. Project Overview

An end-to-end **fully automated job application bot** that:

- 🔍 **Discovers** job listings from LinkedIn, Naukri, Indeed, Glassdoor, ZipRecruiter, Google Jobs, and 40+ ATS career portals
- 🧠 **Tailors** your PDF resume using Claude Code AI for every individual job description
- 🤖 **Applies** automatically using Playwright browser automation — forms, file uploads, multi-step flows
- 📧 **Notifies** you via email after each application with the tailored resume attached
- 💰 **Costs $0** — fully powered by your Claude Code subscription + free open-source tools

---

## 2. Tech Stack

| Layer | Tool | Cost | Notes |
|---|---|---|---|
| **AI Engine** | Claude Code (your subscription) | $0 | Resume tailoring, Q&A answering, intelligence |
| **Job Scraping** | python-jobspy | $0 | LinkedIn, Indeed, Glassdoor, Google Jobs, Naukri, ZipRecruiter |
| **Extra Jobs** | Adzuna API + The Muse API + Remotive | $0 | Free API keys |
| **Browser Automation** | Playwright (Python) | $0 | Form filling, file uploads |
| **Anti-Detection** | playwright-stealth + undetected-playwright | $0 | Bot evasion |
| **PDF Parsing** | PyMuPDF4LLM | $0 | Resume → Markdown |
| **PDF Generation** | Jinja2 + WeasyPrint | $0 | Tailored resume → PDF |
| **Database** | SQLite (local) | $0 | Job tracking, deduplication |
| **Email** | Gmail SMTP (smtplib) | $0 | 100 notifications/day free |
| **Scheduling** | APScheduler + cron | $0 | Daily automation |
| **Hosting** | Your local machine OR Oracle Cloud Free ARM | $0 | 4 core, 24 GB RAM forever free |
| **Orchestration** | Python scripts + Claude Code agents | $0 | Claude manages the pipeline |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY SCHEDULER (APScheduler)             │
│                    Runs at 8:00 AM every day                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────▼───────────┐
          │   PHASE 1: DISCOVER   │
          │   python-jobspy       │
          │   + Adzuna API        │
          │   → SQLite DB         │
          └───────────┬───────────┘
                      │ New jobs only (deduplication)
          ┌───────────▼───────────┐
          │   PHASE 2: FILTER     │
          │   Claude Code scores  │
          │   job relevance 1-10  │
          │   Skip score < 6      │
          └───────────┬───────────┘
                      │ Jobs scored ≥ 6
          ┌───────────▼───────────┐
          │   PHASE 3: TAILOR     │
          │   PyMuPDF4LLM parses  │
          │   your base resume    │
          │   Claude Code rewrites│
          │   for each job        │
          │   WeasyPrint → PDF    │
          └───────────┬───────────┘
                      │ Tailored PDF ready
          ┌───────────▼───────────┐
          │   PHASE 4: APPLY      │
          │   Playwright opens    │
          │   browser, fills form │
          │   uploads PDF, submits│
          │   (per-platform logic)│
          └───────────┬───────────┘
                      │ Application confirmed
          ┌───────────▼───────────┐
          │   PHASE 5: NOTIFY     │
          │   Gmail SMTP sends    │
          │   email with job info │
          │   + PDF attached      │
          │   DB status = APPLIED │
          └───────────────────────┘
```

---

## 4. Project Structure

```
job-bot/
│
├── 📄 README.md
├── 📄 requirements.txt
├── 📄 .env                          # Credentials (never commit)
├── 📄 config.yaml                   # Job preferences, filters
│
├── 📁 data/
│   ├── base_resume.pdf              # Your original resume
│   ├── resume_template.html         # Jinja2 HTML template for PDF
│   └── jobs.db                      # SQLite database
│
├── 📁 tailored_resumes/             # Auto-generated per application
│   └── resume_Google_SWE_2024.pdf
│
├── 📁 src/
│   ├── __init__.py
│   │
│   ├── 📁 discovery/
│   │   ├── jobspy_scraper.py        # JobSpy multi-platform scraping
│   │   ├── adzuna_scraper.py        # Adzuna API
│   │   ├── muse_scraper.py          # The Muse API
│   │   ├── deduplicator.py          # Hash-based deduplication
│   │   └── job_scorer.py            # Claude Code job relevance scorer
│   │
│   ├── 📁 resume/
│   │   ├── pdf_parser.py            # PyMuPDF4LLM: PDF → Markdown
│   │   ├── claude_tailor.py         # Claude Code resume rewriter
│   │   ├── pdf_generator.py         # Jinja2 + WeasyPrint → PDF
│   │   └── templates/
│   │       └── resume.html          # ATS-friendly HTML template
│   │
│   ├── 📁 applicator/
│   │   ├── base_adapter.py          # Abstract base class
│   │   ├── linkedin_adapter.py      # LinkedIn Easy Apply
│   │   ├── naukri_adapter.py        # Naukri.com apply flow
│   │   ├── indeed_adapter.py        # Indeed apply flow
│   │   ├── greenhouse_adapter.py    # Greenhouse ATS (API-based)
│   │   ├── lever_adapter.py         # Lever ATS
│   │   ├── workday_adapter.py       # Workday (complex multi-step)
│   │   ├── generic_adapter.py       # Fallback for unknown forms
│   │   └── question_answerer.py     # Claude Code answers custom Q's
│   │
│   ├── 📁 notification/
│   │   └── email_sender.py          # Gmail SMTP with PDF attachment
│   │
│   ├── 📁 database/
│   │   ├── models.py                # SQLite schema
│   │   └── repository.py            # CRUD operations
│   │
│   └── 📁 orchestrator/
│       ├── pipeline.py              # Main pipeline controller
│       └── scheduler.py             # APScheduler config
│
├── 📁 logs/
│   └── app.log
│
└── 📁 tests/
    ├── test_scraper.py
    ├── test_tailor.py
    └── test_applicator.py
```

---

## Phase 1 — Foundation Setup

**Goal:** Get the project skeleton running with config, database, and base resume parsing.

### Tasks
- [ ] Create project directory and virtual environment
- [ ] Install all dependencies (`requirements.txt`)
- [ ] Set up `.env` with credentials (Gmail, API keys)
- [ ] Set up `config.yaml` with job search preferences
- [ ] Create SQLite database schema
- [ ] Test PyMuPDF4LLM parsing your base resume
- [ ] Verify Claude Code CLI works from Python subprocess

### Key Files to Build
- `requirements.txt`
- `.env` template
- `config.yaml`
- `src/database/models.py`
- Basic `main.py` entry point

### config.yaml example
```yaml
job_search:
  keywords:
    - "Python Developer"
    - "Backend Engineer"
    - "Django Developer"
  locations:
    - "Remote"
    - "Bangalore"
    - "Mumbai"
  experience_years: 3
  min_relevance_score: 6       # Claude scores 1-10, skip below this
  max_applications_per_day: 20
  blacklisted_companies:
    - "MLM Company"

platforms:
  linkedin: true
  naukri: true
  indeed: true
  glassdoor: true
  google_jobs: true
  ziprecruiter: false

schedule:
  run_time: "08:00"            # Daily run time
  timezone: "Asia/Kolkata"

applicant_profile:
  name: "Your Name"
  email: "your@email.com"
  phone: "+91-XXXXXXXXXX"
  linkedin_url: "https://linkedin.com/in/yourprofile"
  work_authorization: "Yes"
  willing_to_relocate: false
  expected_salary: "15-20 LPA"
  notice_period: "30 days"
```

---

## Phase 2 — Job Discovery

**Goal:** Scrape fresh jobs daily from all platforms and store with deduplication.

### Tasks
- [ ] Implement JobSpy scraper with all platforms enabled
- [ ] Add Adzuna API integration (free key at developer.adzuna.com)
- [ ] Add The Muse API (free key, 3,600 req/hour)
- [ ] Build deduplication using SHA256 hash of `title+company+location`
- [ ] Build Claude Code job scorer (calls Claude to rate relevance 1-10)
- [ ] Test end-to-end: scrape → deduplicate → score → store in DB

### Database Schema
```sql
CREATE TABLE jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hash TEXT UNIQUE NOT NULL,           -- dedup key
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  platform TEXT,
  job_url TEXT,
  description TEXT,
  relevance_score INTEGER,             -- Claude's score 1-10
  status TEXT DEFAULT 'DISCOVERED',   -- DISCOVERED → TAILORING → APPLYING → APPLIED → FAILED → SKIPPED
  tailored_resume_path TEXT,
  applied_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Claude Code Scoring Prompt
```
You are a job relevance scorer. Rate how well this job matches the candidate profile.

CANDIDATE PROFILE: {profile_summary}
JOB TITLE: {title}
JOB DESCRIPTION: {description[:500]}

Return ONLY a JSON: {"score": 7, "reason": "Good match for Python skills"}
Score 1-10. 10 = perfect match. Below 6 = reject.
```

---

## Phase 3 — AI Resume Tailoring

**Goal:** Use Claude Code to rewrite resume sections for each job, then generate a clean PDF.

### Tasks
- [ ] Build `pdf_parser.py` using PyMuPDF4LLM (resume → Markdown)
- [ ] Build `claude_tailor.py` — calls Claude Code via subprocess
- [ ] Create ATS-friendly HTML resume template (`resume.html`)
- [ ] Build `pdf_generator.py` using Jinja2 + WeasyPrint
- [ ] Test: upload sample job description → get tailored PDF

### Claude Code Tailoring Prompt
```
You are an expert resume writer. Tailor this resume for the job below.

RULES (STRICT):
1. NEVER add skills, experience, or achievements not in the original
2. DO reorder bullet points to emphasize relevant experience first
3. DO mirror keywords from the job description naturally
4. DO rewrite the summary/objective section for this specific role
5. Keep truthful and professional

ORIGINAL RESUME (Markdown):
{resume_markdown}

JOB TITLE: {job_title}
COMPANY: {company}
JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON matching this schema:
{
  "name": "...",
  "contact": {"email": "...", "phone": "...", "linkedin": "..."},
  "summary": "...",
  "experience": [
    {
      "title": "...", "company": "...", "duration": "...",
      "bullets": ["...", "..."]
    }
  ],
  "education": [{"degree": "...", "institution": "...", "year": "..."}],
  "skills": ["...", "..."],
  "projects": [{"name": "...", "description": "...", "tech": "..."}]
}
```

### HTML Resume Template Principles
- Single-column layout (ATS-safe)
- Standard fonts: Arial or Calibri
- No images, icons, or tables in content areas
- Selectable text only (no text as image)
- Standard section headers: Experience, Education, Skills

---

## Phase 4 — Browser Automation

**Goal:** Automatically fill and submit job applications on every supported platform.

### Tasks
- [ ] Build `base_adapter.py` abstract class
- [ ] Build `linkedin_adapter.py` — Easy Apply multi-step modal
- [ ] Build `naukri_adapter.py` — Naukri apply flow
- [ ] Build `indeed_adapter.py` — Indeed apply (redirects + native)
- [ ] Build `greenhouse_adapter.py` — API-based (no browser needed!)
- [ ] Build `lever_adapter.py` — Standard HTML form
- [ ] Build `workday_adapter.py` — Multi-page form flow
- [ ] Build `question_answerer.py` — Claude answers custom questions
- [ ] Build `generic_adapter.py` — AI-powered fallback for unknown forms

### Base Adapter Interface
```python
class BaseAdapter:
    def detect(self, url: str) -> bool:
        """Return True if this adapter handles the URL"""
        raise NotImplementedError

    def login(self, browser_context) -> bool:
        """Log in to the platform"""
        raise NotImplementedError

    def apply(self, job: dict, resume_pdf_path: str) -> bool:
        """Fill and submit the application. Return True if successful."""
        raise NotImplementedError
```

### ATS URL Pattern Detection
```python
ATS_PATTERNS = {
    "greenhouse":   r"boards\.greenhouse\.io",
    "lever":        r"jobs\.lever\.co",
    "workday":      r".*\.wd\d+\.myworkday\.com",
    "icims":        r".*\.icims\.com",
    "taleo":        r".*\.taleo\.net",
    "smartrecruiters": r"jobs\.smartrecruiters\.com",
    "bamboohr":     r".*\.bamboohr\.com",
    "linkedin":     r"linkedin\.com/jobs",
    "naukri":       r"naukri\.com",
    "indeed":       r"indeed\.com",
}
```

### Claude Code for Custom Application Questions
```python
def answer_custom_question(question: str, job_info: dict, profile: dict) -> str:
    prompt = f"""
    Answer this job application question professionally and concisely.

    QUESTION: {question}
    JOB: {job_info['title']} at {job_info['company']}
    CANDIDATE PROFILE: {json.dumps(profile)}

    Rules:
    - Be honest, never fabricate experience
    - Keep answers under 150 words unless asked for more
    - Match the tone to the company culture if identifiable
    - Return ONLY the answer text, nothing else
    """
    result = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True)
    return result.stdout.strip()
```

---

## Phase 5 — Email Notifications

**Goal:** Send a rich email after every successful application with job details + tailored PDF.

### Tasks
- [ ] Set up Gmail App Password (2-Step Verification → App Passwords)
- [ ] Build `email_sender.py` with PDF attachment support
- [ ] Design HTML email template with job info
- [ ] Test: trigger manually with a dummy application

### Email Content Per Notification
```
Subject: ✅ Applied — {Job Title} at {Company Name}

Body:
  🏢 Company:     Google
  💼 Job Title:   Senior Python Developer
  🌐 Platform:    LinkedIn
  📅 Applied at:  March 15, 2026 at 08:23 AM
  🔗 Job URL:     https://linkedin.com/jobs/...
  📎 Attached:    resume_Google_SeniorPythonDev.pdf (tailored)

  Relevance Score: 8/10
  Key matched skills: Python, Django, REST APIs, PostgreSQL
```

---

## Phase 6 — Orchestration & Scheduling

**Goal:** Wire all phases into one automated daily pipeline.

### Tasks
- [ ] Build `pipeline.py` as the main controller
- [ ] Add proper error handling and retry logic
- [ ] Add rate limiting between applications (60-second delays)
- [ ] Set up APScheduler for daily runs
- [ ] Set up logging to `logs/app.log`
- [ ] Add daily summary email (total applied, failed, skipped)

### Pipeline Flow (pipeline.py)
```python
def run_daily_pipeline():
    log.info("=== Daily Job Bot Pipeline Starting ===")

    # Step 1: Discover new jobs
    new_jobs = discover_jobs()
    log.info(f"Discovered {len(new_jobs)} new jobs")

    # Step 2: Score and filter
    scored_jobs = [j for j in new_jobs if score_job(j) >= config.min_score]
    log.info(f"{len(scored_jobs)} jobs passed relevance filter")

    # Step 3: Apply to each (max daily limit)
    applied = 0
    for job in scored_jobs[:config.max_applications_per_day]:
        try:
            # Tailor resume
            tailored_pdf = tailor_resume(job)

            # Apply
            success = apply_to_job(job, tailored_pdf)

            if success:
                # Notify
                send_notification(job, tailored_pdf)
                mark_applied(job)
                applied += 1
                time.sleep(random.randint(45, 90))  # Human-like delay

        except Exception as e:
            log.error(f"Failed to apply to {job['title']} at {job['company']}: {e}")
            mark_failed(job)

    # Step 4: Daily summary
    send_daily_summary(applied)
    log.info(f"=== Pipeline Complete. Applied to {applied} jobs ===")
```

---

## Phase 7 — Anti-Detection & Safety

**Goal:** Avoid account bans on LinkedIn, Naukri, and Indeed.

### Anti-Detection Checklist
- [ ] Use `playwright-stealth` plugin on all browser instances
- [ ] Use `launchPersistentContext` to reuse browser profiles (not fresh each time)
- [ ] Run in headed mode (not headless) for LinkedIn
- [ ] Add randomized 45–90 second delays between applications
- [ ] Add realistic mouse movement simulation
- [ ] Only run during business hours (8 AM – 9 PM)
- [ ] Never exceed daily limits per platform

### Daily Limits Per Platform (Safe)
| Platform | Safe Daily Limit | Notes |
|---|---|---|
| LinkedIn | 10–15 applications | Most aggressive detection |
| Indeed | 20–30 applications | Moderate detection |
| Naukri | 20–40 applications | Lighter detection |
| Greenhouse | Unlimited | API-based, no browser |
| Lever | 10–20 applications | hCaptcha on suspicious activity |
| Workday | 5–10 applications | Complex forms, go slow |

### Account Safety Rules
1. **Never run LinkedIn on datacenter IPs** — use your home IP only
2. **Mix organic activity** — occasionally manually like posts or connect with people
3. **Start slow** — first week: max 5 applications/day. Scale up gradually
4. **Log everything** — if an account gets flagged, you need the audit trail
5. **Separate accounts** — consider a dedicated job-hunt LinkedIn account

---

## Phase 8 — Testing & Launch

**Goal:** Test every component in isolation, then run end-to-end dry runs before going live.

### Testing Checklist
- [ ] Unit test: JobSpy scraping (verify results from each platform)
- [ ] Unit test: Resume parsing (verify Markdown output quality)
- [ ] Unit test: Claude Code tailoring (verify JSON structure)
- [ ] Unit test: PDF generation (verify visual output)
- [ ] Unit test: Email sending (send to yourself)
- [ ] Integration test: Dry run with 3 jobs, `apply=False` flag
- [ ] Integration test: Apply to 1 real job manually supervised
- [ ] Full E2E test: Run pipeline with 5-job limit, watch browser
- [ ] Production launch: Enable scheduler, set daily limit to 10

### Dry Run Mode
Add a `DRY_RUN=true` env flag that:
- Scrapes real jobs ✅
- Scores and tailors resumes ✅
- Opens browser and fills forms ✅
- **Stops before clicking Submit** ⛔
- Still sends you the notification email with the tailored PDF ✅

---

## Platform Coverage

### Tier 1 — Direct Integration (Fully Automated)
| Platform | Method | Difficulty |
|---|---|---|
| LinkedIn Easy Apply | Playwright (modal flow) | Medium |
| Indeed Apply | Playwright (native + redirect) | Medium |
| Naukri.com | Playwright (form flow) | Medium |
| Greenhouse | REST API (no browser!) | Easy |
| Lever | Playwright (HTML form) | Easy |

### Tier 2 — Browser Automation (Automated with care)
| Platform | Method | Difficulty |
|---|---|---|
| Workday | Playwright (multi-page React) | Hard |
| iCIMS | Playwright (legacy UI) | Medium |
| SmartRecruiters | Playwright (modern form) | Easy |
| BambooHR | Playwright (clean form) | Easy |
| Taleo (Oracle) | Playwright (legacy, fragile) | Hard |

### Tier 3 — API Only (No browser needed)
| Platform | Method |
|---|---|
| Glassdoor | JobSpy scrape only (apply redirects to company site) |
| Adzuna | Discovery API only |
| The Muse | Discovery API only |
| RemoteOK | Discovery API only |

---

## Daily Limits & Rates

```
Target:  20 tailored applications/day
Cost:    $0 (Claude Code subscription covers AI)
Time:    ~2-3 hours to process (running in background)

Breakdown per application:
  Job scraping:        ~1 sec
  Claude scoring:      ~3 sec
  Resume parsing:      ~0.5 sec
  Claude tailoring:    ~8 sec
  PDF generation:      ~1 sec
  Browser apply:       60-90 sec (with human delays)
  Email notification:  ~1 sec
  ─────────────────────────────
  Total per job:       ~75-105 sec

20 jobs/day × 90 sec avg = ~30 minutes actual automation time
```

---

## Risk & Mitigation

| Risk | Probability | Mitigation |
|---|---|---|
| LinkedIn account ban | Medium | Daily limit ≤15, headed mode, residential IP, slow pacing |
| Indeed CAPTCHA block | Low-Medium | playwright-stealth, randomized delays |
| Naukri bot detection | Low | Conservative pacing |
| Claude Code rate limits | Low | Add 5-second delay between Claude calls |
| Workday form changes | Medium | Log HTML changes, alert when form fails |
| Wrong answer to custom Q | Low | Claude answers from profile, review logs |
| Duplicate applications | Low | SQLite deduplication prevents re-applying |
| PDF formatting breaks | Low | Validate PDF visually before first live run |

---

## Getting Started — Quick Setup

```bash
# 1. Clone / create project
mkdir job-bot && cd job-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install python-jobspy pymupdf4llm playwright weasyprint \
            jinja2 apscheduler python-dotenv pyyaml requests \
            playwright-stealth sqlite3

# 4. Install Playwright browsers
playwright install chromium

# 5. Set up .env
cp .env.example .env
# Edit .env with your credentials

# 6. Add your resume
cp ~/your-resume.pdf data/base_resume.pdf

# 7. Test Claude Code connection
claude -p "Say hello" 

# 8. Run in dry-run mode
DRY_RUN=true python main.py --limit 3

# 9. Check output
ls tailored_resumes/   # Should see generated PDFs
cat logs/app.log       # Check for errors
# Check your email for test notifications

# 10. Go live!
python main.py  # Or enable scheduler
```

---

## Build Order (Recommended)

```
Week 1:  Phase 1 (Foundation) + Phase 2 (Job Discovery)
Week 2:  Phase 3 (Resume Tailoring) — most important
Week 3:  Phase 4 (LinkedIn + Greenhouse adapters first)
Week 4:  Phase 5 (Email) + Phase 6 (Orchestration) + Phase 7 (Anti-detection)
Week 5:  Phase 8 (Testing) → Go live with 5 apps/day → scale up
```

---

*Generated for: Ragiv's Job Bot Project*
*Date: March 2026*
*AI Engine: Claude Code (Anthropic)*
*Total Estimated Cost: $0*
