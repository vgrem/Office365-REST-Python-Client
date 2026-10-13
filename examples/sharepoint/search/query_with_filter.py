"""
Search with property filters — author, date range, and custom managed properties.

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Search with KQL property filters")
    parser.add_argument(
        "--query",
        default='Author:"John Smith" LastModifiedTime>2024-01-01',
        help="KQL query with property filters",
    )
    parser.add_argument("--limit", type=int, default=20, help="maximum number of rows")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    # KQL syntax: Author:"John Smith" AND LastModifiedTime>2024-01-01
    # post_query is used instead of query to avoid URL encoding issues
    # with special KQL characters (quotes, >) in the GET request path
    result = ctx.search.post_query(
        query_text=args.query,
        select_properties=["Path", "Title", "Author", "LastModifiedTime"],
        row_limit=args.limit,
    ).execute_query()
    results = result.value.PrimaryQueryResult.RelevantResults
    rows = list(results.Table.Rows)
    if not rows:
        print(f"No results for query: {args.query}")
        return
    for row in rows:
        print(row.Cells["Path"], row.Cells.get("Author", ""), row.Cells.get("LastModifiedTime", ""))


if __name__ == "__main__":
    main()
