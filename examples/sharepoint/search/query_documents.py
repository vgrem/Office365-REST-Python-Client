"""
Search for document files in a SharePoint tenant.

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Search for documents (IsDocument:1)")
    parser.add_argument("--query", default="IsDocument:1", help="KQL query text")
    parser.add_argument("--limit", type=int, default=10, help="maximum number of rows")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    result = ctx.search.post_query(query_text=args.query, row_limit=args.limit).execute_query()
    results = result.value.PrimaryQueryResult.RelevantResults
    for row in results.Table.Rows:
        print(row.Cells["Path"])


if __name__ == "__main__":
    main()
