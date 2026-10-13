"""
Load cookies exported by Playwright into a SharePoint client context.

The library does not depend on Playwright; this is a helper that demonstrates
how to reuse a browser session captured by ``capture_cookies_with_playwright.py``.

Usage:
    SP_SITE_URL="https://contoso.sharepoint.com/sites/demo" \
    PLAYWRIGHT_STORAGE_STATE="./storage_state.json" \
    python examples/sharepoint/auth/load_cookies_from_playwright.py
"""

import argparse
import json
import os
from typing import Dict

from office365.sharepoint.client_context import ClientContext

SPO_COOKIE_NAMES = {"FedAuth", "rtFa", "SPOIDCRL"}


def load_cookies_from_storage_state(path: str) -> Dict[str, str]:
    """Load cookies exported by Playwright storage_state.json and extract SPO cookies."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cookies = {}
    for c in data.get("cookies", []):
        name = c.get("name")
        if name in SPO_COOKIE_NAMES:
            cookies[name] = c.get("value", "")
    return cookies


def main():
    parser = argparse.ArgumentParser(description="Load a Playwright browser session into ClientContext")
    parser.add_argument(
        "--site-url",
        default=os.environ.get("SP_SITE_URL", "https://contoso.sharepoint.com/sites/demo"),
        help="target site URL",
    )
    parser.add_argument(
        "--storage-state",
        default=os.environ.get("PLAYWRIGHT_STORAGE_STATE", "./storage_state.json"),
        help="path to the Playwright storage_state.json file",
    )
    args = parser.parse_args()

    if not os.path.exists(args.storage_state):
        print(f"Storage state not found: {args.storage_state}")
        print("Capture it first with capture_cookies_with_playwright.py (or pass --storage-state).")
        return

    ctx = ClientContext(args.site_url).with_cookies(lambda: load_cookies_from_storage_state(args.storage_state))
    web = ctx.web.get().execute_query()
    print(f"Web title: {web.title}")


if __name__ == "__main__":
    main()
