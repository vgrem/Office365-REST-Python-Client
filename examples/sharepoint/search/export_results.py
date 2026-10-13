"""
Export search results to a CSV file.

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

import argparse
import csv
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

COLUMNS = ["Path", "Title", "Author", "LastModifiedTime"]


def main():
    parser = argparse.ArgumentParser(description="Export search results to CSV")
    parser.add_argument("--query", default="IsDocument:1", help="KQL query")
    parser.add_argument(
        "--output",
        default=os.path.join(tempfile.gettempdir(), "search_results.csv"),
        help="Output CSV path (default: temp dir)",
    )
    parser.add_argument("--limit", type=int, default=100, help="Maximum results")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    result = ctx.search.query(
        query_text=args.query,
        select_properties=COLUMNS,
        row_limit=args.limit,
    ).execute_query()

    rows = result.value.PrimaryQueryResult.RelevantResults.Table.Rows
    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            cells = row.Cells
            writer.writerow({col: cells.get(col, "") for col in COLUMNS})
    print(f"Exported {len(rows)} results to {args.output}")


if __name__ == "__main__":
    main()
