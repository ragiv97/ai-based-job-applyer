import logging
import time
import random
from playwright.sync_api import BrowserContext, Page
from .base_adapter import BaseAdapter
from .question_answerer import answer_custom_question

log = logging.getLogger(__name__)


class WorkdayAdapter(BaseAdapter):
    def detect(self, url: str) -> bool:
        return "myworkday.com" in url.lower() or "myworkdayjobs.com" in url.lower()

    def login(self, context: BrowserContext) -> bool:
        # Workday typically uses "Sign In" or "Create Account" on each employer's portal
        # Most applications can be done without an account
        return True

    def apply(self, page: Page, job: dict, resume_pdf_path: str, profile: dict) -> bool:
        try:
            page.goto(job["job_url"], wait_until="domcontentloaded")
            time.sleep(random.uniform(3, 5))

            # Click Apply button
            apply_btn = page.locator('a:has-text("Apply"), button:has-text("Apply")').first
            if apply_btn.count() > 0:
                apply_btn.click()
                time.sleep(random.uniform(2, 4))

            # Workday multi-step form
            max_steps = 15
            for step in range(max_steps):
                time.sleep(random.uniform(1, 2))

                # Upload resume if prompted
                file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0 and file_input.is_visible():
                    file_input.set_input_files(resume_pdf_path)
                    time.sleep(2)

                # Fill visible text inputs
                inputs = page.locator('input[type="text"]:visible')
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    if not inp.input_value():
                        label = self._find_label(page, inp)
                        value = self._get_field_value(label, profile, job)
                        if value:
                            inp.fill(value)
                            time.sleep(random.uniform(0.3, 0.6))

                # Fill textareas
                textareas = page.locator("textarea:visible")
                for i in range(textareas.count()):
                    ta = textareas.nth(i)
                    if not ta.input_value():
                        label = self._find_label(page, ta)
                        if label:
                            answer = answer_custom_question(label, job, profile)
                            if answer:
                                ta.fill(answer)
                                time.sleep(random.uniform(0.3, 0.6))

                # Check for Submit
                submit_btn = page.locator('button:has-text("Submit")').first
                if submit_btn.count() > 0 and submit_btn.is_visible():
                    if self._check_dry_run(page, "submit Workday application"):
                        return True
                    submit_btn.click()
                    time.sleep(3)
                    log.info(f"Submitted Workday application for '{job['title']}'")
                    return True

                # Click Next/Continue
                next_btn = page.locator(
                    'button:has-text("Next"), button:has-text("Continue"), button:has-text("Save and Continue")'
                ).first
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    continue

                break

            log.warning(f"Workday flow incomplete for '{job['title']}'")
            return False

        except Exception as e:
            log.error(f"Workday apply error for '{job['title']}': {e}")
            return False

    def _find_label(self, page: Page, element) -> str:
        el_id = element.get_attribute("id")
        if el_id:
            label = page.locator(f'label[for="{el_id}"]')
            if label.count() > 0:
                return label.first.text_content() or ""
        aria = element.get_attribute("aria-label")
        if aria:
            return aria
        placeholder = element.get_attribute("placeholder")
        return placeholder or ""

    def _get_field_value(self, label: str, profile: dict, job: dict) -> str:
        label_lower = label.lower()
        if "first name" in label_lower:
            return profile.get("name", "").split()[0] if profile.get("name") else ""
        if "last name" in label_lower:
            parts = profile.get("name", "").split()
            return parts[-1] if len(parts) > 1 else ""
        if "email" in label_lower:
            return profile.get("email", "")
        if "phone" in label_lower or "mobile" in label_lower:
            return profile.get("phone", "")
        if "linkedin" in label_lower:
            return profile.get("linkedin_url", "")
        return ""
