import logging
import os
import time
import random
from playwright.sync_api import BrowserContext, Page
from .base_adapter import BaseAdapter
from .question_answerer import answer_custom_question

log = logging.getLogger(__name__)


class LinkedInAdapter(BaseAdapter):
    def detect(self, url: str) -> bool:
        return "linkedin.com" in url.lower()

    def login(self, context: BrowserContext) -> bool:
        page = context.new_page()
        try:
            page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            time.sleep(random.uniform(1, 2))

            email = os.getenv("LINKEDIN_EMAIL", "")
            password = os.getenv("LINKEDIN_PASSWORD", "")
            if not email or not password:
                log.error("LinkedIn credentials not set in .env")
                return False

            page.fill("#username", email)
            time.sleep(random.uniform(0.5, 1))
            page.fill("#password", password)
            time.sleep(random.uniform(0.5, 1))
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)

            if "feed" in page.url or "mynetwork" in page.url:
                log.info("LinkedIn login successful")
                return True

            # Check for security checkpoint
            if "checkpoint" in page.url:
                log.warning("LinkedIn security checkpoint detected - manual intervention needed")
                return False

            log.warning(f"LinkedIn login may have failed, current URL: {page.url}")
            return False
        except Exception as e:
            log.error(f"LinkedIn login error: {e}")
            return False
        finally:
            page.close()

    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        try:
            page.goto(job["job_url"], wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 4))

            # Click Easy Apply button
            easy_apply_btn = page.locator('button:has-text("Easy Apply")').first
            if not easy_apply_btn.is_visible():
                log.info(f"No Easy Apply button for '{job['title']}' - skipping")
                return False

            easy_apply_btn.click()
            time.sleep(random.uniform(1, 2))

            # Handle multi-step modal
            max_steps = 10
            for step in range(max_steps):
                time.sleep(random.uniform(1, 2))

                # Upload resume if file input is present
                file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0:
                    file_input.set_input_files(resume_pdf_path)
                    time.sleep(1)

                # Fill text inputs that are empty
                text_inputs = page.locator('input[type="text"]:visible')
                for i in range(text_inputs.count()):
                    inp = text_inputs.nth(i)
                    if not inp.input_value():
                        label = inp.get_attribute("aria-label") or ""
                        value = self._get_profile_value(label, profile, job)
                        if value:
                            inp.fill(value)
                            time.sleep(random.uniform(0.3, 0.6))

                # Answer textarea questions
                textareas = page.locator("textarea:visible")
                for i in range(textareas.count()):
                    ta = textareas.nth(i)
                    if not ta.input_value():
                        label = ta.get_attribute("aria-label") or ta.get_attribute("placeholder") or ""
                        if label:
                            answer = answer_custom_question(label, job, profile)
                            if answer:
                                ta.fill(answer)
                                time.sleep(random.uniform(0.3, 0.6))

                # Check for Submit button
                submit_btn = page.locator('button:has-text("Submit application")').first
                if submit_btn.count() > 0 and submit_btn.is_visible():
                    if self._check_dry_run(page, "submit LinkedIn application"):
                        return True
                    submit_btn.click()
                    time.sleep(2)
                    log.info(f"Submitted LinkedIn application for '{job['title']}'")
                    return True

                # Click Next/Review button
                next_btn = page.locator('button:has-text("Next"), button:has-text("Review")').first
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    continue

                # If no next or submit found, try to close and skip
                break

            log.warning(f"LinkedIn Easy Apply flow did not complete for '{job['title']}'")
            return False

        except Exception as e:
            log.error(f"LinkedIn apply error for '{job['title']}': {e}")
            return False

    def _get_profile_value(self, label: str, profile: dict, job: dict) -> str:
        label_lower = label.lower()
        if "phone" in label_lower or "mobile" in label_lower:
            return profile.get("phone", "")
        if "email" in label_lower:
            return profile.get("email", "")
        if "linkedin" in label_lower:
            return profile.get("linkedin_url", "")
        if "salary" in label_lower:
            return profile.get("expected_salary", "")
        if "notice" in label_lower:
            return profile.get("notice_period", "")
        return ""
