#!/usr/bin/env python3
"""Copy cookies from your real Chrome browser into the bot's Playwright browser profile."""

import json
import os
import shutil
import sqlite3
import tempfile
import time

# Chrome cookie domains we need
TARGET_DOMAINS = [
    ".linkedin.com",
    ".www.linkedin.com",
    ".naukri.com",
    ".www.naukri.com",
    ".indeed.com",
    ".secure.indeed.com",
    "linkedin.com",
    "www.linkedin.com",
    "naukri.com",
    "www.naukri.com",
    "indeed.com",
    "secure.indeed.com",
]

CHROME_COOKIE_DB = os.path.expanduser(
    "~/Library/Application Support/Google/Chrome/Default/Cookies"
)

BROWSER_DATA_DIR = os.path.join(os.path.dirname(__file__), "browser_data")


def extract_chrome_cookies() -> list[dict]:
    """Extract cookies from Chrome's SQLite database."""
    if not os.path.exists(CHROME_COOKIE_DB):
        print(f"Chrome cookie database not found at {CHROME_COOKIE_DB}")
        return []

    # Copy the DB since Chrome locks it
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2(CHROME_COOKIE_DB, tmp)

    cookies = []
    try:
        conn = sqlite3.connect(tmp)
        # Chrome's cookie schema
        cursor = conn.execute(
            """SELECT host_key, name, path, expires_utc, is_secure, is_httponly,
                      samesite, value
               FROM cookies
               WHERE host_key LIKE '%linkedin.com%'
                  OR host_key LIKE '%naukri.com%'
                  OR host_key LIKE '%indeed.com%'"""
        )

        for row in cursor.fetchall():
            host, name, path, expires, secure, httponly, samesite, value = row

            # Chrome stores expiry as microseconds since Jan 1 1601
            # Convert to Unix epoch seconds
            if expires:
                expires_unix = (expires / 1_000_000) - 11644473600
            else:
                expires_unix = -1

            sameSite_map = {0: "None", 1: "Lax", 2: "Strict"}

            cookie = {
                "name": name,
                "value": value,
                "domain": host,
                "path": path or "/",
                "expires": expires_unix if expires_unix > 0 else -1,
                "httpOnly": bool(httponly),
                "secure": bool(secure),
                "sameSite": sameSite_map.get(samesite, "Lax"),
            }
            cookies.append(cookie)

        conn.close()
    finally:
        os.unlink(tmp)

    return cookies


def inject_cookies_into_playwright(cookies: list[dict]):
    """Launch Playwright with persistent context and inject cookies."""
    from playwright.sync_api import sync_playwright

    os.makedirs(BROWSER_DATA_DIR, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            BROWSER_DATA_DIR,
            channel="chrome",
            headless=True,
            viewport={"width": 1280, "height": 800},
        )

        # Add cookies to the browser context
        playwright_cookies = []
        for c in cookies:
            pc = {
                "name": c["name"],
                "value": c["value"],
                "domain": c["domain"],
                "path": c["path"],
                "httpOnly": c["httpOnly"],
                "secure": c["secure"],
                "sameSite": c["sameSite"],
            }
            if c["expires"] > 0:
                pc["expires"] = c["expires"]
            playwright_cookies.append(pc)

        if playwright_cookies:
            context.add_cookies(playwright_cookies)

        context.close()


def main():
    print("=== Copying cookies from Chrome to Job Bot ===\n")

    # Make sure Chrome is closed for clean DB access
    print("NOTE: Close Chrome first for a clean cookie copy.\n")

    cookies = extract_chrome_cookies()

    linkedin_count = sum(1 for c in cookies if "linkedin" in c["domain"])
    naukri_count = sum(1 for c in cookies if "naukri" in c["domain"])
    indeed_count = sum(1 for c in cookies if "indeed" in c["domain"])

    print(f"Found cookies:")
    print(f"  LinkedIn: {linkedin_count}")
    print(f"  Naukri:   {naukri_count}")
    print(f"  Indeed:   {indeed_count}")
    print(f"  Total:    {len(cookies)}\n")

    if not cookies:
        print("No cookies found. Make sure you're logged into these sites in Chrome.")
        return

    print("Injecting cookies into bot browser...")
    inject_cookies_into_playwright(cookies)
    print("Done! Sessions copied to browser_data/")


if __name__ == "__main__":
    main()
