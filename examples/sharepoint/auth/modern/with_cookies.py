"""
Connect to SharePoint using browser-session cookies (FedAuth / rtFa).

This is useful when you already have authenticated browser cookies
(e.g. from Playwright, Selenium, or a logged-in browser session).
Cookie values are read from ``SP_FEDAUTH`` / ``SP_RTFA``; to capture them from a
real browser see ``capture_cookies_with_playwright.py``.

See https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-api
"""

import argparse
import os

from office365.sharepoint.client_context import ClientContext
from tests.settings import site_url


def main():
    argparse.ArgumentParser(description="Connect to SharePoint using browser-session cookies").parse_args()

    cookies = {
        "FedAuth": os.environ.get("SP_FEDAUTH", ""),
        "rtFa": os.environ.get("SP_RTFA", ""),
    }
    if not cookies["FedAuth"]:
        print("Set SP_FEDAUTH (and optionally SP_RTFA) to a captured browser cookie.")
        print("See capture_cookies_with_playwright.py / load_cookies_from_playwright.py.")
        return

    ctx = ClientContext(site_url).with_cookies(lambda: cookies)
    web = ctx.web.get().execute_query()
    print(web.url)


if __name__ == "__main__":
    main()
