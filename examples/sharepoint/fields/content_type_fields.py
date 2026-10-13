"""
Link a field to a content type and list the content type's field links.

A content type's *field links* select which columns appear on items.

REST restriction: a field can be linked to a content type only if it already
exists on the content type's parent. To surface a brand-new site column on a
list, add the column to the list first (its default content types pick it up
automatically), then link it to derived content types.

https://learn.microsoft.com/en-us/previous-versions/office/sharepoint-visio/jj245869(v=office.15)
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

DEMO_NAME = "ZZ Field Link Demo"


def main():
    parser = argparse.ArgumentParser(description="Link a field to a content type")
    parser.add_argument("--content-type", default="Item", help="Parent content type (the field must exist on it)")
    parser.add_argument("--field", default="Title", help="Field internal name or title")
    parser.add_argument("--keep", action="store_true", help="Keep the demo content type (default: delete after demo)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    # Remove a leftover demo content type from a previous run.
    stale = ctx.web.content_types.find_by_name(DEMO_NAME)
    try:
        stale.get().execute_query()
        stale.delete_object().execute_query()
    except Exception:
        pass

    # Create a scratch content type derived from the parent.
    parent = ctx.web.content_types.find_by_name(args.content_type, required=True)
    parent.ensure_property("StringId").execute_query()
    ctx.web.content_types.create(DEMO_NAME, parent_content_type=parent.string_id)
    ctx.execute_query()

    content_type = ctx.web.content_types.find_by_name(DEMO_NAME)
    content_type.get().execute_query()
    print(f"Content type created: {content_type.name}  ({content_type.string_id})")

    # Link the field. It must already exist on the parent content type.
    field = ctx.web.fields.get_by_internal_name_or_title(args.field)
    try:
        content_type.field_links.add(field).execute_query()
    except Exception as e:
        if not args.keep:
            content_type.delete_object().execute_query()
        raise SystemExit(
            f"Cannot link '{args.field}': it must already exist on parent '{args.content_type}'.\n{e}"
        ) from e
    print(f"Field linked: {args.field}")

    links = content_type.field_links.get().execute_query()
    print(f"\nField links ({len(links)}):")
    for link in links:
        print(f"  {link.name or link.field_internal_name}")

    if not args.keep:
        content_type.delete_object().execute_query()
        print("\n  (content type removed after demo)")


if __name__ == "__main__":
    main()
