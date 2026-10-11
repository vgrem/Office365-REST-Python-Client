"""
Publishing workflow — check in, publish, and verify state.

The two-step publish workflow for site pages: check the page in (making the
latest version visible) and publish it, then confirm the resulting publishing
level.

Requires delegated permission ``Sites.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/sitepage-checkin
https://learn.microsoft.com/en-us/graph/api/sitepage-publish
"""

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, client_secret, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Check in and publish a site page")
    parser.add_argument("--site-url", default=site_url, help="site URL (default: root site)")
    parser.add_argument("--keep", action="store_true", help="keep the page after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    site = client.sites.get_by_url(args.site_url)

    # -- Step 1: create a page --
    page = site.pages.add(title=create_unique_name("Release-Notes")).execute_query()
    print(f"Page created: '{page.title}'")

    # -- Step 2: check it in (makes the latest version available) --
    page.checkin("Initial version").execute_query()
    print("  ✓ Checked in")

    # -- Step 3: publish it --
    page.publish().execute_query()
    print("  ✓ Published")

    # -- Step 4: verify the publishing state --
    page = page.get().select(["publishingState"]).execute_query()
    level = page.publishing_state.level
    version = page.publishing_state.versionId
    print(f"\n  publishingState.level = {level}")
    print(f"  publishingState.versionId = {version}")

    if not args.keep:
        page.delete_object().execute_query()
        print("\nPage deleted.")


if __name__ == "__main__":
    main()
