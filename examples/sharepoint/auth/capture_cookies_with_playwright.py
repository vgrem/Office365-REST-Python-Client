"""
Acquire SharePoint Online browser-session cookies using Playwright and save them into
storage_state.json (or a custom path), which can be consumed by examples/sharepoint/auth/load_cookies_from_playwright.py.

Requirements (not installed by the library):
  pip install playwright
  playwright install chromium

Usage:
  SP_SITE_URL="https://contoso.sharepoint.com/sites/demo" \
  PLAYWRIGHT_STORAGE_STATE="./storage_state.json" \
  HEADLESS=false \
  python examples/sharepoint/auth/capture_cookies_with_playwright.py

Notes:
- The script opens a browser window. Complete the Microsoft login (including MFA) manually.
- It polls for the FedAuth cookie and saves the state as soon as authentication completes.
- The resulting storage_state.json can be used by load_cookies_from_playwright.py.
"""

import os
import time

from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]


def main() -> None:
    site_url = os.environ.get("SP_SITE_URL")
    if not site_url:
        raise SystemExit("SP_SITE_URL is required, e.g. https://contoso.sharepoint.com/sites/demo")

    storage_state_path = os.environ.get("PLAYWRIGHT_STORAGE_STATE", "./storage_state.json")
    headless_env = os.environ.get("HEADLESS", "false").lower()
    headless = headless_env in ("1", "true", "yes")
    timeout_seconds = int(os.environ.get("LOGIN_TIMEOUT", "180"))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto(site_url)
        # Wait for network to be idle; login flow may redirect to Microsoft login pages
        page.wait_for_load_state("networkidle")

        print("\nA browser window is open. Complete the login (including MFA) if prompted.")
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if any(cookie.get("name") == "FedAuth" for cookie in context.cookies()):
                print("Authentication detected.")
                break
            page.wait_for_timeout(1000)
        else:
            print(f"Timed out after {timeout_seconds}s waiting for the FedAuth cookie; saving whatever was captured.")

        # Persist cookies and related state
        context.storage_state(path=storage_state_path)
        print(f"Saved Playwright storage state to: {storage_state_path}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
