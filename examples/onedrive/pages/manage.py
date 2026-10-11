"""
Site pages — create, get, update, publish, and delete.

The full page lifecycle in a SharePoint site, from creation through publishing.

Requires delegated permission ``Sites.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/sitepage-create
https://learn.microsoft.com/en-us/graph/api/sitepage-publish
"""

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, client_secret, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Create, update, publish and delete a site page")
    parser.add_argument("--site-url", default=site_url, help="site URL to create the page in (default: root site)")
    parser.add_argument("--keep", action="store_true", help="keep the page after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    site = client.sites.get_by_url(args.site_url)

    # -- Step 1: create a page --
    page_name = create_unique_name("Status-Report")
    page = site.pages.add(title=page_name).execute_query()
    print(f"Page created: '{page.title}'")

    # -- Step 2: find it back by title --
    found = site.pages.find_by_title(page_name, required=True).execute_query()
    print(f"  Found by title: '{found.title}'")

    # -- Step 3: update page properties --
    found.set_property("showComments", True)
    found.set_property("showRecommendedPages", True)
    found.update().execute_query()
    print(f"  Updated: show_comments={found.show_comments}, show_recommended={found.show_recommended_pages}")

    # -- Step 4: publish --
    found.publish().execute_query()
    print("  ✓ Published")

    # -- Step 5: list all pages --
    pages = site.pages.get().execute_query()
    print(f"\nSite pages ({len(pages)}):")
    for p in pages:
        print(f"  {p.title}")

    if not args.keep:
        found.delete_object().execute_query()
        print("\nPage deleted.")


if __name__ == "__main__":
    main()
