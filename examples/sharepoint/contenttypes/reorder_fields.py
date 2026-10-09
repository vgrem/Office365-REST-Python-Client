"""
Change the display order of fields in a content type.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Reorder fields in a content type")
    parser.add_argument("--name", required=True, help="Content type name")
    parser.add_argument("--order", nargs="+", required=True, help="Field internal names in desired order")
    parser.add_argument("--keep", action="store_true", help="Keep the content type (default: delete after demo)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    ct = ctx.web.ensure_content_type(name=args.name).execute_query()

    # Link any field that is not already part of the content type
    existing = {link.field_internal_name for link in ct.field_links.get().execute_query()}
    for field_name in args.order:
        if field_name in existing:
            continue
        field = ctx.web.fields.get_by_internal_name_or_title(field_name)
        ct.field_links.add(field).execute_query()
        print(f"Field added: {field_name}")

    ct.reorder_fields(args.order).execute_query()
    print(f"Fields reordered: {' -> '.join(args.order)}")

    if not args.keep:
        ct.delete_object().execute_query()
        print("  (content type removed after demo)")


if __name__ == "__main__":
    main()
