"""
Sort search results using the SharePoint Search REST service.

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.sort.sort import Sort
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Sort search results by a managed property")
    parser.add_argument("--property", default="LastModifiedTime", help="managed property to sort by")
    parser.add_argument("--direction", type=int, default=1, choices=[0, 1], help="0 = ascending, 1 = descending")
    parser.add_argument("--limit", type=int, default=20, help="maximum number of rows")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    result = ctx.search.query(
        query_text="IsDocument:1",
        sort_list=[Sort(Property=args.property, Direction=args.direction)],
        select_properties=["Path", "LastModifiedTime"],
        row_limit=args.limit,
    ).execute_query()

    results = result.value.PrimaryQueryResult.RelevantResults
    for row in results.Table.Rows:
        print(row.Cells["Path"], row.Cells["LastModifiedTime"])


if __name__ == "__main__":
    main()
