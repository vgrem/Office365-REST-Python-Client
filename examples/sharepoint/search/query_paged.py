"""
Paginate through large search results using ``start_row`` and ``row_limit``.

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Page through search results")
    parser.add_argument("--query", default="IsDocument:1", help="KQL query text")
    parser.add_argument("--page-size", type=int, default=50, help="rows per page")
    parser.add_argument("--max-results", type=int, default=200, help="safety cap on total rows")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    start_row = 0
    total = 0
    while total < args.max_results:
        result = ctx.search.query(
            query_text=args.query,
            start_row=start_row,
            row_limit=args.page_size,
            select_properties=["Path", "Title"],
        ).execute_query()
        relevant = result.value.PrimaryQueryResult.RelevantResults
        rows = relevant.Table.Rows
        if not rows:
            break
        for row in rows:
            total += 1
            print(f"[{total}] {row.Cells['Path']}")
        start_row += len(rows)
    print(f"Total results fetched: {total}")


if __name__ == "__main__":
    main()
