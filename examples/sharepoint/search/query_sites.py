"""
Search SharePoint sites where the current user is a member.

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Search for sites (contentclass:STS_Site)")
    parser.add_argument("--limit", type=int, default=20, help="maximum number of rows")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    result = ctx.search.query("contentclass:STS_Site", row_limit=args.limit).execute_query()
    results = result.value.PrimaryQueryResult.RelevantResults
    for row in results.Table.Rows:
        print(row.Cells["Path"])  # prints site url


if __name__ == "__main__":
    main()
