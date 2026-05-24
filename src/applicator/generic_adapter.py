import logging
import time
import random
from playwright.sync_api import BrowserContext, Page
from .base_adapter import BaseAdapter
from .question_answerer import answer_custom_question

log = logging.getLogger(__name__)


class GenericAdapter(BaseAdapter):
    """Fallback adapter that attempts to fill any job application form using heuristics."""

    def detect(self, url: str) -> bool:
        return True  # Catches everything not matched by specific adapters

    def login(self, context: BrowserContext) -> bool:
        return True

    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        try:
            page.goto(job["job_url"], wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 4))

            # Look for any Apply button
            apply_btn = page.locator(
                'a:has-text("Apply"), button:has-text("Apply"), '
                'a:has-text("Apply Now"), button:has-text("Apply Now")'
            ).first
            if apply_btn.count() > 0 and apply_btn.is_visible():
                apply_btn.click()
                time.sleep(random.uniform(2, 3))

            # Fill form fields using heuristics
            self._fill_name_fields(page, profile)
            self._fill_contact_fields(page, profile)
            self._upload_resume(page, resume_pdf_path)
            self._fill_questions(page, job, profile)

            # Look for submit button
            submit_btn = page.locator(
                'button[type="submit"], input[type="submit"], '
                'button:has-text("Submit"), button:has-text("Apply")'
            ).first
            if submit_btn.count() > 0 and submit_btn.is_visible():
                if self._check_dry_run(page, "submit generic application"):
                    return True
                submit_btn.click()
                time.sleep(2)
                log.info(f"Submitted generic application for '{job['title']}'")
                return True

            log.warning(f"Generic adapter could not find submit button for '{job['title']}'")
            return False

        except Exception as e:
            log.error(f"Generic apply error for '{job['title']}': {e}")
            return False

    def _fill_name_fields(self, page: Page, profile: dict):
        name = profile.get("name", "")
        parts = name.split() if name else []

        name_selectors = [
            ('input[name*="first_name"], input[name*="firstName"], input[placeholder*="First"]',
             parts[0] if parts else ""),
            ('input[name*="last_name"], input[name*="lastName"], input[placeholder*="Last"]',
             parts[-1] if len(parts) > 1 else ""),
            ('input[name*="full_name"], input[name*="fullName"], input[name="name"]',
             name),
        ]

        for selector, value in name_selectors:
            if value:
                field = page.locator(selector).first
                if field.count() > 0 and not field.input_value():
                    field.fill(value)
                    time.sleep(random.uniform(0.2, 0.4))

    def _fill_contact_fields(self, page: Page, profile: dict):
        contact_selectors = [
            ('input[name*="email"], input[type="email"]', profile.get("email", "")),
            ('input[name*="phone"], input[type="tel"]', profile.get("phone", "")),
            ('input[name*="linkedin"], input[placeholder*="LinkedIn"]', profile.get("linkedin_url", "")),
        ]

        for selector, value in contact_selectors:
            if value:
                field = page.locator(selector).first
                if field.count() > 0 and not field.input_value():
                    field.fill(value)
                    time.sleep(random.uniform(0.2, 0.4))

    def _upload_resume(self, page: Page, resume_pdf_path: str):
        file_input = page.locator('input[type="file"]').first
        if file_input.count() > 0:
            file_input.set_input_files(resume_pdf_path)
            time.sleep(1)

    def _fill_questions(self, page: Page, job: dict, profile: dict):
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
