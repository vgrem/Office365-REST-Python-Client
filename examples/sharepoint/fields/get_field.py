"""
Get a field (column) by name and inspect its definition, including schema XML.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Inspect a field definition")
    parser.add_argument("--list-title", default="Documents", help="List containing the field")
    parser.add_argument("--field", default="Title", help="Field internal name or title")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    field = ctx.web.lists.get_by_title(args.list_title).fields.get_by_internal_name_or_title(args.field)
    ctx.load(
        field,
        [
            "SchemaXml",
            "Title",
            "InternalName",
            "FieldTypeKind",
            "TypeDisplayName",
            "Required",
            "Hidden",
            "Group",
            "Indexed",
        ],
    ).execute_query()

    print(f"Field: {field.title}  (type: {field.type_display_name or field.field_type_kind.name})")
    print(f"  Internal name: {field.internal_name}")
    print(f"  Group: {field.group or '?'}")
    print(f"  Required: {field.properties.get('Required', False)}  Hidden: {field.hidden}  Indexed: {field.indexed}")
    print(f"  SchemaXml:\n{field.schema_xml}")


if __name__ == "__main__":
    main()
