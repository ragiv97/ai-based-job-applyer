import logging
import os
import time
import random
from playwright.sync_api import BrowserContext, Page
from .base_adapter import BaseAdapter

log = logging.getLogger(__name__)


class NaukriAdapter(BaseAdapter):
    def detect(self, url: str) -> bool:
        return "naukri.com" in url.lower()

    def login(self, context: BrowserContext) -> bool:
        page = context.new_page()
        try:
            page.goto("https://www.naukri.com/nlogin/login", wait_until="domcontentloaded")
            time.sleep(random.uniform(1, 2))

            email = os.getenv("NAUKRI_EMAIL", "")
            password = os.getenv("NAUKRI_PASSWORD", "")
            if not email or not password:
                log.error("Naukri credentials not set in .env")
                return False

            page.fill('input[placeholder="Enter your active Email ID / Username"]', email)
            time.sleep(random.uniform(0.5, 1))
            page.fill('input[placeholder="Enter your password"]', password)
            time.sleep(random.uniform(0.5, 1))
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)

            if "naukri.com" in page.url and "login" not in page.url:
                log.info("Naukri login successful")
                return True

            log.warning(f"Naukri login may have failed, current URL: {page.url}")
            return False
        except Exception as e:
            log.error(f"Naukri login error: {e}")
            return False
        finally:
            page.close()

    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        try:
            page.goto(job["job_url"], wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 4))

            # Look for Apply button
            apply_btn = page.locator('button:has-text("Apply"), a:has-text("Apply")').first
            if apply_btn.count() == 0 or not apply_btn.is_visible():
                log.info(f"No Apply button found on Naukri for '{job['title']}'")
                return False

            apply_btn.click()
            time.sleep(random.uniform(2, 3))

            # Handle resume upload if prompted
            file_input = page.locator('input[type="file"]').first
            if file_input.count() > 0:
                file_input.set_input_files(resume_pdf_path)
                time.sleep(1)

            # Look for submit/apply confirmation
            submit_btn = page.locator(
                'button:has-text("Submit"), button:has-text("Apply"), button:has-text("Confirm")'
            ).first
            if submit_btn.count() > 0 and submit_btn.is_visible():
                if self._check_dry_run(page, "submit Naukri application"):
                    return True
                submit_btn.click()
                time.sleep(2)
                log.info(f"Submitted Naukri application for '{job['title']}'")
                return True

            # Check if already applied (Naukri shows "Already Applied")
            if page.locator('text="Already Applied"').count() > 0:
                log.info(f"Already applied on Naukri for '{job['title']}'")
                return False

            log.warning(f"Naukri apply flow incomplete for '{job['title']}'")
            return False

        except Exception as e:
            log.error(f"Naukri apply error for '{job['title']}': {e}")
            return False
