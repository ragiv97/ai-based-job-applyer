#!/usr/bin/env python3
"""Manual login helper — log into platforms once, session is saved for future runs.
Opens all three platforms in separate tabs. Log in manually, then close the browser."""

import os
import sys
import time

def main():
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    browser_data_dir = os.path.join(os.path.dirname(__file__), "browser_data")
    os.makedirs(browser_data_dir, exist_ok=True)

    urls = [
        ("LinkedIn", "https://www.linkedin.com/login"),
        ("Naukri", "https://www.naukri.com/nlogin/login"),
        ("Indeed", "https://secure.indeed.com/auth"),
    ]

    print("\n=== Job Bot — Manual Login Setup ===")
    print("Opening LinkedIn, Naukri, and Indeed in separate tabs.")
    print("Log into each one manually (SSO/Google/whatever).")
    print("When done, just CLOSE THE BROWSER WINDOW.")
    print("Sessions will be saved automatically.\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            browser_data_dir,
            channel="chrome",  # Use installed Chrome instead of Playwright Chromium
            headless=False,
            viewport={"width": 1280, "height": 800},
        )

        stealth = Stealth()
        for name, url in urls:
            page = context.new_page()
            stealth.apply_stealth_sync(page)
            page.goto(url, wait_until="domcontentloaded")
            print(f"  Opened: {name}")

        # Close the default blank tab
        if len(context.pages) > 3:
            context.pages[0].close()

        print("\n>>> Log into all platforms, then close the browser window.")

        # Wait until the browser is closed by the user
        try:
            while context.pages:
                time.sleep(1)
        except Exception:
            pass

    print("\nDone! Sessions saved to browser_data/")


if __name__ == "__main__":
    main()
