"""
Copy a site column to another site (or list) by reusing its schema XML.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, team_site_url, tenant


def make_ctx(url: str) -> ClientContext:
    return ClientContext(url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )


def main():
    parser = argparse.ArgumentParser(description="Copy a field via its schema XML")
    parser.add_argument("--field", required=True, help="Field internal name or title")
    parser.add_argument("--source", default=team_site_url, help="Source site URL")
    parser.add_argument("--target", default=site_url, help="Target site URL")
    parser.add_argument("--list-title", help="Target list (default: site columns)")
    parser.add_argument("--keep", action="store_true", help="Keep the copied field (default: delete after demo)")
    args = parser.parse_args()

    source = make_ctx(args.source)
    source_field = source.web.fields.get_by_internal_name_or_title(args.field)
    source.load(source_field, ["SchemaXml"]).execute_query()
    schema_xml = source_field.schema_xml_for_copy()
    if schema_xml is None:
        raise SystemExit(f"Field '{args.field}' not found in the source site.")

    target = make_ctx(args.target)
    scope = target.web.fields
    if args.list_title:
        scope = target.web.lists.get_by_title(args.list_title).fields
    copied = scope.create_field_as_xml(schema_xml).execute_query()
    scope_name = "site column" if not args.list_title else args.list_title
    print(f"Copied '{args.field}' as '{copied.internal_name}' ({scope_name})")

    if not args.keep:
        copied.delete_object().execute_query()
        print("  (copied field removed after demo)")


if __name__ == "__main__":
    main()
