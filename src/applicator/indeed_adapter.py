import logging
import os
import time
import random
from playwright.sync_api import BrowserContext, Page
from .base_adapter import BaseAdapter
from .question_answerer import answer_custom_question

log = logging.getLogger(__name__)


class IndeedAdapter(BaseAdapter):
    def detect(self, url: str) -> bool:
        return "indeed.com" in url.lower()

    def login(self, context: BrowserContext) -> bool:
        page = context.new_page()
        try:
            page.goto("https://secure.indeed.com/auth", wait_until="domcontentloaded")
            time.sleep(random.uniform(1, 2))

            email = os.getenv("INDEED_EMAIL", "")
            password = os.getenv("INDEED_PASSWORD", "")
            if not email or not password:
                log.error("Indeed credentials not set in .env")
                return False

            page.fill('input[name="__email"]', email)
            page.click('button[type="submit"]')
            time.sleep(random.uniform(2, 3))

            page.fill('input[name="__password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle", timeout=15000)

            if "indeed.com" in page.url and "auth" not in page.url:
                log.info("Indeed login successful")
                return True

            log.warning(f"Indeed login may have failed, current URL: {page.url}")
            return False
        except Exception as e:
            log.error(f"Indeed login error: {e}")
            return False
        finally:
            page.close()

    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        try:
            page.goto(job["job_url"], wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 4))

            # Click Apply Now button
            apply_btn = page.locator('button:has-text("Apply now"), a:has-text("Apply now")').first
            if apply_btn.count() == 0 or not apply_btn.is_visible():
                log.info(f"No Apply Now button on Indeed for '{job['title']}'")
                return False

            apply_btn.click()
            time.sleep(random.uniform(2, 3))

            # Handle multi-step Indeed apply flow
            max_steps = 8
            for step in range(max_steps):
                time.sleep(random.uniform(1, 2))

                # Upload resume if prompted
                file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0:
                    file_input.set_input_files(resume_pdf_path)
                    time.sleep(1)

                # Fill empty text fields
                text_inputs = page.locator('input[type="text"]:visible')
                for i in range(text_inputs.count()):
                    inp = text_inputs.nth(i)
                    if not inp.input_value():
                        label_el = page.locator(f'label[for="{inp.get_attribute("id")}"]')
                        label = label_el.text_content() if label_el.count() > 0 else ""
                        value = self._get_profile_value(label, profile)
                        if value:
                            inp.fill(value)
                            time.sleep(random.uniform(0.3, 0.6))

                # Answer textarea questions
                textareas = page.locator("textarea:visible")
                for i in range(textareas.count()):
                    ta = textareas.nth(i)
                    if not ta.input_value():
                        label = ta.get_attribute("aria-label") or ""
                        if label:
                            answer = answer_custom_question(label, job, profile)
                            if answer:
                                ta.fill(answer)

                # Check for submit
                submit_btn = page.locator(
                    'button:has-text("Submit your application"), button:has-text("Submit")'
                ).first
                if submit_btn.count() > 0 and submit_btn.is_visible():
                    if self._check_dry_run(page, "submit Indeed application"):
                        return True
                    submit_btn.click()
                    time.sleep(2)
                    log.info(f"Submitted Indeed application for '{job['title']}'")
                    return True

                # Click Continue
                continue_btn = page.locator(
                    'button:has-text("Continue"), button:has-text("Next")'
                ).first
                if continue_btn.count() > 0 and continue_btn.is_visible():
                    continue_btn.click()
                    continue

                break

            log.warning(f"Indeed apply flow incomplete for '{job['title']}'")
            return False

        except Exception as e:
            log.error(f"Indeed apply error for '{job['title']}': {e}")
            return False

    def _get_profile_value(self, label: str, profile: dict) -> str:
        label_lower = label.lower()
        if "phone" in label_lower:
            return profile.get("phone", "")
        if "email" in label_lower:
            return profile.get("email", "")
        if "salary" in label_lower:
            return profile.get("expected_salary", "")
        return ""
