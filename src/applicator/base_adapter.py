import logging
import os
import re
from abc import ABC, abstractmethod
from playwright.sync_api import BrowserContext, Page

log = logging.getLogger(__name__)

ATS_PATTERNS = {
    "greenhouse": r"boards\.greenhouse\.io",
    "lever": r"jobs\.lever\.co",
    "workday": r".*\.wd\d+\.myworkday\.com",
    "icims": r".*\.icims\.com",
    "taleo": r".*\.taleo\.net",
    "smartrecruiters": r"jobs\.smartrecruiters\.com",
    "bamboohr": r".*\.bamboohr\.com",
    "linkedin": r"linkedin\.com/jobs",
    "naukri": r"naukri\.com",
    "indeed": r"indeed\.com",
}


class BaseAdapter(ABC):
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run or os.getenv("DRY_RUN", "false").lower() == "true"

    @abstractmethod
    def detect(self, url: str) -> bool:
        """Return True if this adapter handles the URL."""
        raise NotImplementedError

    @abstractmethod
    def login(self, context: BrowserContext) -> bool:
        """Log in to the platform. Return True if successful."""
        raise NotImplementedError

    @abstractmethod
    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        """Fill and submit the application. Return True if successful."""
        raise NotImplementedError

    def _check_dry_run(self, page: Page, action: str = "submit") -> bool:
        """If dry run, log and return False to prevent submission."""
        if self.dry_run:
            log.info(f"DRY RUN: Would {action} but stopping before submit")
            return True
        return False


def detect_platform(url: str) -> str:
    """Detect which platform/ATS a job URL belongs to."""
    for platform, pattern in ATS_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return platform
    return "generic"
