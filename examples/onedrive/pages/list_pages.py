"""
List site pages with their publishing state.

Enumerate the pages in a site, showing the publishing level of each — useful
for content governance and finding draft pages that were never published.

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/graph/api/sitepage-list
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="List site pages with publishing state")
    parser.add_argument("--site-url", default=site_url, help="site URL (default: root site)")
    parser.add_argument("--top", type=int, default=50, help="max pages to list (default: 50)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    site = client.sites.get_by_url(args.site_url)

    pages = site.pages.select(["title", "name", "publishingState"]).top(args.top).get().execute_query()
    print(f"Site pages ({len(pages)}):")
    drafts = 0
    for p in pages:
        level = p.publishing_state.level or "?"
        if level != "published":
            drafts += 1
        print(f"  {p.title:45s}  {level}")
    print(f"\nDrafts / not published: {drafts}")


if __name__ == "__main__":
    main()
