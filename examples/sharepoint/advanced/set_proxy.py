"""
Demonstrates how to configure a proxy for all SharePoint REST API requests.

Proxy is set at the transport level, ensuring it applies to ALL requests
including internal ones (form digest).

For MSAL authentication requests to login.microsoftonline.com, set the
``HTTPS_PROXY`` environment variable instead — MSAL reads it automatically.

Usage:
    export HTTPS_PROXY="http://proxy:8080"
    python set_proxy.py

See https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-api
"""

import argparse
import os

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Configure an HTTP proxy for all SharePoint requests")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    parser.add_argument(
        "--proxy",
        default=os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "",
        help="proxy URL, e.g. http://proxy:8080 (defaults to HTTPS_PROXY)",
    )
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    if args.proxy:
        ctx.with_transport(proxies={"http": args.proxy, "https": args.proxy})
        print(f"Using proxy: {args.proxy}")
    else:
        print("No proxy configured (set --proxy or HTTPS_PROXY); connecting directly.")

    web = ctx.web.get().execute_query()
    print(f"Connected to: {web.url}")


if __name__ == "__main__":
    main()
