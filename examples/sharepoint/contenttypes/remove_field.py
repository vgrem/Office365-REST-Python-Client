"""
Remove a field link from a content type.

Note: SharePoint's REST API accepts the DELETE but does not remove a field link
that the content type inherits from its parent, so this example re-reads the
links and reports whether the removal actually took effect.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Remove a field from a content type")
    parser.add_argument("--name", required=True, help="Content type name")
    parser.add_argument("--field", required=True, help="Field internal name or title")
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
    field = ctx.web.fields.get_by_internal_name_or_title(args.field)
    ctx.load(field, ["InternalName"]).execute_query()

    links = ct.field_links.get().execute_query()
    target = next((link for link in links if link.field_internal_name == field.internal_name), None)
    if target is None:
        raise SystemExit(f"Field '{args.field}' is not linked to content type '{args.name}'")
    target.delete_object().execute_query()

    # Re-read: a DELETE on an inherited field link returns 200 but has no effect.
    remaining = ct.field_links.get().execute_query()
    if any(link.field_internal_name == field.internal_name for link in remaining):
        print(
            f"Note: '{field.internal_name}' is still linked — a field link inherited from a parent "
            "content type cannot be removed through the REST API."
        )
    else:
        print(f"Field removed from content type: {field.internal_name}")
    print(f"Field links remaining: {len(remaining)}")

    if created and not args.keep:
        ct.delete_object().execute_query()
        print("  (content type removed after demo)")


if __name__ == "__main__":
    main()
