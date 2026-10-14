"""
Change the display order of fields in a content type.

Only fields that are **already linked** to the content type can be ordered:
SharePoint Online's REST API cannot attach a brand-new column to a content
type, so any requested field that is not linked yet is reported and skipped.
The requested order is merged with the remaining linked fields so that no link
is dropped.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Reorder fields in a content type")
    parser.add_argument("--name", required=True, help="Content type name")
    parser.add_argument("--order", nargs="+", required=True, help="Field internal names in desired order")
    parser.add_argument(
        "--keep", action="store_true", help="Keep the content type (default: delete only if created here)"
    )
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    existing = ctx.web.content_types.find_by_name(args.name)
    existing.execute_query()
    created = not existing.is_loaded
    ct = ctx.web.ensure_content_type(name=args.name).execute_query()

    linked = [link.field_internal_name for link in ct.field_links.get().execute_query() if link.field_internal_name]
    missing = [name for name in args.order if name not in linked]
    if missing:
        print(f"Not linked (skipped, REST cannot attach a new column): {', '.join(missing)}")

    requested = [name for name in args.order if name in linked]
    new_order = requested + [name for name in linked if name not in requested]
    ct.reorder_fields(new_order).execute_query()
    print(f"Fields reordered: {' -> '.join(new_order)}")

    if created and not args.keep:
        ct.delete_object().execute_query()
        print("  (content type removed after demo)")


if __name__ == "__main__":
    main()
