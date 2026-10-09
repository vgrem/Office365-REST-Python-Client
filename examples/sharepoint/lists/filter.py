"""Filter a list collection with an OData expression.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Filter lists by an OData expression")
    parser.add_argument("--filter", default="IsSystemList eq false", help="OData $filter expression")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    lists = ctx.web.lists.select(["IsSystemList", "Title"]).filter(args.filter).execute_query()
    print(f"{len(lists)} list(s):")
    for lst in lists:
        print(f"  {lst.title}")


if __name__ == "__main__":
    main()
