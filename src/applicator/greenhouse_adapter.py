import logging
import os
import re
import requests
from playwright.sync_api import BrowserContext, Page
from .base_adapter import BaseAdapter

log = logging.getLogger(__name__)


class GreenhouseAdapter(BaseAdapter):
    """Greenhouse ATS - supports both API-based and browser-based applications."""

    def detect(self, url: str) -> bool:
        return "greenhouse.io" in url.lower()

    def login(self, context: BrowserContext) -> bool:
        # Greenhouse doesn't require login for applications
        return True

    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        url = job["job_url"]

        # Try API-based application first
        job_id = self._extract_job_id(url)
        if job_id:
            result = self._apply_via_api(job_id, resume_pdf_path, profile)
            if result:
                return result

        # Fallback to browser-based
        return self._apply_via_browser(page, job, resume_pdf_path, profile)

    def _extract_job_id(self, url: str) -> str:
        match = re.search(r'/jobs/(\d+)', url)
        return match.group(1) if match else ""

    def _apply_via_api(self, job_id: str, resume_pdf_path: str, profile: dict) -> bool:
        """Apply using Greenhouse's public job board API."""
        try:
            api_url = f"https://boards-api.greenhouse.io/v1/boards/unknown/jobs/{job_id}"
            # Note: The board token needs to be extracted from the job URL
            # This is a simplified version - real implementation would parse the board name
            log.info(f"Greenhouse API application not available for job {job_id}, using browser")
            return False
        except Exception as e:
            log.error(f"Greenhouse API error: {e}")
            return False

    def _apply_via_browser(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        try:
            page.goto(job["job_url"], wait_until="domcontentloaded")
            import time, random
            time.sleep(random.uniform(2, 3))

            # Fill standard Greenhouse form fields
            field_mapping = {
                'input[name="job_application[first_name]"]': profile.get("name", "").split()[0] if profile.get("name") else "",
                'input[name="job_application[last_name]"]': profile.get("name", "").split()[-1] if profile.get("name") else "",
                'input[name="job_application[email]"]': profile.get("email", ""),
                'input[name="job_application[phone]"]': profile.get("phone", ""),
            }

            for selector, value in field_mapping.items():
                if value:
                    field = page.locator(selector).first
                    if field.count() > 0:
                        field.fill(value)
                        time.sleep(random.uniform(0.2, 0.5))

            # Upload resume
            file_input = page.locator('input[type="file"]').first
            if file_input.count() > 0:
                file_input.set_input_files(resume_pdf_path)
                time.sleep(1)

            # LinkedIn URL if field exists
            linkedin_field = page.locator('input[name*="linkedin"], input[placeholder*="LinkedIn"]').first
            if linkedin_field.count() > 0 and profile.get("linkedin_url"):
                linkedin_field.fill(profile["linkedin_url"])

            # Submit
            submit_btn = page.locator('input[type="submit"], button[type="submit"]').first
            if submit_btn.count() > 0:
                if self._check_dry_run(page, "submit Greenhouse application"):
                    return True
                submit_btn.click()
                time.sleep(2)
                log.info(f"Submitted Greenhouse application for '{job['title']}'")
                return True

            log.warning(f"Greenhouse submit button not found for '{job['title']}'")
            return False

        except Exception as e:
            log.error(f"Greenhouse browser apply error for '{job['title']}': {e}")
            return False
