"""
Retrieve a content type by name or by id.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Get a content type by name or id")
    parser.add_argument("--name", help="Content type name")
    parser.add_argument("--id", help="Content type id")
    args = parser.parse_args()

    if not args.name and not args.id:
        raise SystemExit("Provide --name or --id")

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    if args.name:
        ct = ctx.web.content_types.find_by_name(args.name, required=True)
    else:
        assert args.id is not None
        ct = ctx.web.content_types.get_by_id(args.id)
    ctx.load(ct, ["Name", "Description", "Id", "StringId"]).execute_query()

    print(f"Name: {ct.name}")
    print(f"Description: {ct.description}")
    print(f"ID: {ct.id}")
    print(f"String ID: {ct.string_id}")


if __name__ == "__main__":
    main()
