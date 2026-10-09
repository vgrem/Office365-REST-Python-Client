"""Read list items using an OData filter query.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse
import datetime

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Read list items using an OData filter")
    parser.add_argument("--list-title", default="Site Pages", help="list title")
    parser.add_argument("--since", default="2022-01-20", help="only items created after this date")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    since = datetime.datetime.fromisoformat(args.since)
    filter_text = f"Created gt datetime'{since.isoformat()}'"
    items = (
        ctx.web.lists.get_by_title(args.list_title)
        .items.filter(filter_text)
        .select(["Created", "EncodedAbsUrl"])
        .get()
        .execute_query()
    )
    print(f"Loaded items count: {len(items)}")
    for item in items:
        print(f"  {item.properties['EncodedAbsUrl']}")


if __name__ == "__main__":
    main()
