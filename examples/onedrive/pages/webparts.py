"""
Web parts — list and inspect the web parts on a page.

Shows how to enumerate the web parts of a page (including their type and
position) so you can introspect page content or target a specific web part.

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/graph/api/sitepage-get-webparts
https://learn.microsoft.com/en-us/graph/api/webpart-getpositionofwebpart
"""

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, client_secret, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="List the web parts on a site page")
    parser.add_argument("--site-url", default=site_url, help="site URL (default: root site)")
    parser.add_argument("--keep", action="store_true", help="keep the page after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    site = client.sites.get_by_url(args.site_url)

    # -- Step 1: create a fresh page to inspect --
    page = site.pages.add(title=create_unique_name("WebParts-Demo")).execute_query()
    print(f"Page: '{page.title}'")

    # -- Step 2: list web parts via the collection --
    web_parts = page.web_parts.get().execute_query()
    print(f"Web parts ({len(web_parts)}):")
    for wp in web_parts:
        wp_type = type(wp).__name__
        title = wp.get_property("innerHtml") or wp.get_property("title") or ""
        print(f"  {wp_type:15s}  {str(title)[:60]}")

    # -- Step 3: resolve the position of each web part --
    if web_parts:
        print("\nPositions:")
        for wp in web_parts:
            position = wp.get_position_of_web_part().execute_query().value
            print(f"  section={position.horizontalSectionId}  column={position.columnId}  index={position.webPartIndex}")

    if not args.keep:
        page.delete_object().execute_query()
        print("\nPage deleted.")


if __name__ == "__main__":
    main()
