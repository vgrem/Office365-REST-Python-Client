"""
End-to-end content type workflow: create a content type, add a field,
associate it with a list, and verify.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.contenttypes.creation_information import ContentTypeCreationInformation
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Content type end-to-end workflow")
    parser.add_argument("--name", default="ZZ ContentType Demo", help="Content type name")
    parser.add_argument("--description", default="For Contoso projects", help="Content type description")
    parser.add_argument("--list-title", default="Documents", help="List to associate the content type with")
    parser.add_argument("--keep", action="store_true", help="Keep the content type and list binding")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    # 1. Create the content type
    info = ContentTypeCreationInformation(Name=args.name, Description=args.description)
    ct = ctx.web.content_types.add(info).execute_query()
    if ct.string_id is None:
        raise SystemExit("Failed to create content type")
    print(f"1. Created: {ct.name}  (id: {ct.string_id})")

    # 2. Add a site column (field) to the content type. 'Title' is inherited
    #    from the Item parent, so this link is idempotent — SharePoint Online's
    #    REST API cannot attach a brand-new column to a content type.
    field = ctx.web.fields.get_by_internal_name_or_title("Title")
    ct.field_links.add(field).execute_query()
    print(f"2. Added field: {field.internal_name}")

    # 3. Associate the content type with a list
    target_list = ctx.web.lists.get_by_title(args.list_title)
    target_list.content_types.add(ContentTypeCreationInformation(Name=args.name, Id=ct.string_id)).execute_query()
    print(f"3. Associated with list: {args.list_title}")

    # 4. Verify the content types on the list
    list_cts = target_list.content_types.get().execute_query()
    print(f"4. Content types on '{args.list_title}': {[c.name for c in list_cts]}")

    if not args.keep:
        list_ct = target_list.content_types.find_by_name(args.name)
        list_ct.execute_query()
        if list_ct.is_loaded:
            list_ct.delete_object().execute_query()
        ct.delete_object().execute_query()
        print("  (content type and list binding removed after demo)")


if __name__ == "__main__":
    main()
