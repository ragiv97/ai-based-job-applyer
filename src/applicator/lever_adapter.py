import logging
import time
import random
from playwright.sync_api import BrowserContext, Page
from .base_adapter import BaseAdapter

log = logging.getLogger(__name__)


class LeverAdapter(BaseAdapter):
    def detect(self, url: str) -> bool:
        return "lever.co" in url.lower()

    def login(self, context: BrowserContext) -> bool:
        # Lever doesn't require login
        return True

    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        try:
            # Navigate to the apply page
            apply_url = job["job_url"]
            if "/apply" not in apply_url:
                apply_url = apply_url.rstrip("/") + "/apply"

            page.goto(apply_url, wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 3))

            # Fill standard Lever form fields
            name_parts = profile.get("name", "").split()
            field_fills = [
                ('input[name="name"]', profile.get("name", "")),
                ('input[name="email"]', profile.get("email", "")),
                ('input[name="phone"]', profile.get("phone", "")),
                ('input[name="org"]', ""),  # Current company - leave empty or fill
                ('input[name="urls[LinkedIn]"]', profile.get("linkedin_url", "")),
            ]

            for selector, value in field_fills:
                if value:
                    field = page.locator(selector).first
                    if field.count() > 0:
                        field.fill(value)
                        time.sleep(random.uniform(0.2, 0.5))

            # Upload resume
            file_input = page.locator('input[type="file"][name="resume"]').first
            if file_input.count() > 0:
                file_input.set_input_files(resume_pdf_path)
                time.sleep(1)

            # Submit
            submit_btn = page.locator('button[type="submit"]:has-text("Submit"), button:has-text("Submit application")').first
            if submit_btn.count() > 0:
                if self._check_dry_run(page, "submit Lever application"):
                    return True
                submit_btn.click()
                time.sleep(2)
                log.info(f"Submitted Lever application for '{job['title']}'")
                return True

            log.warning(f"Lever submit button not found for '{job['title']}'")
            return False

        except Exception as e:
            log.error(f"Lever apply error for '{job['title']}': {e}")
            return False
