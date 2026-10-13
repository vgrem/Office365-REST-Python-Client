"""
Print the top navigation bar of a SharePoint site.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/navigation-api-reference
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Print the top navigation bar of a site")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    nav = ctx.web.navigation.top_navigation_bar.get().execute_query()
    for item in nav:
        print(f"{item.title}  ({item.url})")


if __name__ == "__main__":
    main()
