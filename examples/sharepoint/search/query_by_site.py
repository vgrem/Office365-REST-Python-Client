"""
Search for document files within a specific site.

The ``Path`` managed property is provided to limit the search scope.

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Search for documents within a site")
    parser.add_argument("--scope", default=team_site_url, help="site URL to scope the query to")
    parser.add_argument("--limit", type=int, default=10, help="maximum number of rows")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    result = ctx.search.post_query(f"Path:{args.scope}", row_limit=args.limit).execute_query()
    for row in result.value.PrimaryQueryResult.RelevantResults.Table.Rows:
        print("{0}".format(row.Cells["Path"]))


if __name__ == "__main__":
    main()
