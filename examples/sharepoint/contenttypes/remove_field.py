"""
Remove a field link from a content type.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Remove a field from a content type")
    parser.add_argument("--name", required=True, help="Content type name")
    parser.add_argument("--field", required=True, help="Field internal name or title")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    ct = ctx.web.ensure_content_type(name=args.name).execute_query()
    field = ctx.web.fields.get_by_internal_name_or_title(args.field)
    ctx.load(field, ["InternalName"]).execute_query()

    links = ct.field_links.get().execute_query()
    target = next((link for link in links if link.field_internal_name == field.internal_name), None)
    if target is None:
        raise SystemExit(f"Field '{args.field}' is not linked to content type '{args.name}'")
    target.delete_object().execute_query()
    print(f"Field removed from content type: {field.internal_name}")

    remaining = ct.field_links.get().execute_query()
    print(f"Field links remaining: {len(remaining)}")


if __name__ == "__main__":
    main()
