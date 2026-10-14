"""
Clone a content type to another site, including its custom fields.

Reads the source content type (metadata + field links), recreates it on
the target site — optionally from the same parent — and re-adds each
field, creating the site column on the target when it does not exist
yet (via its schema XML).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse
from typing import Optional

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.contenttypes.creation_information import ContentTypeCreationInformation
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, team_site_url, tenant


def make_ctx(url: str) -> ClientContext:
    return ClientContext(url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )


def _create_content_type(target: ClientContext, name: str, description: str, group: str, parent_name: Optional[str]):
    parent = None
    if parent_name:
        parent = target.web.content_types.find_by_name(parent_name, required=True)
        parent.execute_query()
    if parent is not None:
        ct = target.web.content_types.create(
            name=name, description=description, group=group, parent_content_type=parent
        ).execute_query()
        print(f"Created '{name}' from parent '{parent_name}' ({ct.string_id})")
        return ct
    info = ContentTypeCreationInformation(Name=name, Description=description, Group=group)
    ct = target.web.content_types.add(info).execute_query()
    print(f"Created '{name}' ({ct.string_id})")
    return ct


def main():
    parser = argparse.ArgumentParser(description="Clone a content type to another site")
    parser.add_argument("--name", required=True, help="Content type name")
    parser.add_argument("--source", default=team_site_url, help="Source site URL")
    parser.add_argument("--target", default=site_url, help="Target site URL")
    parser.add_argument("--parent", default=None, help="Parent content type on the target (default: source parent name)")
    parser.add_argument("--keep", action="store_true", help="Keep the cloned content type (default: delete after demo)")
    args = parser.parse_args()

    source = make_ctx(args.source)
    source_ct = source.web.content_types.find_by_name(args.name, required=True)
    source.load(source_ct, ["Name", "Description", "Group", "StringId", "Parent/Name"]).execute_query()
    if source_ct.name is None:
        raise SystemExit(f"Content type '{args.name}' not found in the source site.")
    parent_name = source_ct.parent.name if source_ct.parent else None

    links = source_ct.field_links.get().execute_query()
    field_names = [link.field_internal_name for link in links if link.field_internal_name]
    print(f"Source: {source_ct.name}  fields={field_names}")

    target = make_ctx(args.target)
    new_ct = _create_content_type(
        target, args.name, source_ct.description or "", source_ct.group or "", args.parent or parent_name
    )

    for field_name in field_names:
        try:
            field = target.web.fields.get_by_internal_name_or_title(field_name)
            target.load(field, ["Id", "InternalName"]).execute_query()
            print(f"  reused field: {field_name}")
        except ClientRequestException:
            src_field = source.web.fields.get_by_internal_name_or_title(field_name)
            source.load(src_field, ["SchemaXml"]).execute_query()
            schema = src_field.schema_xml_for_copy()
            if not schema:
                print(f"  skip: no schema for '{field_name}'")
                continue
            field = target.web.fields.create_field_as_xml(schema).execute_query()
            print(f"  created field: {field_name}")
        new_ct.field_links.add(field).execute_query()

    if not args.keep:
        new_ct.delete_object().execute_query()
        print("  (cloned content type removed after demo)")


if __name__ == "__main__":
    main()
