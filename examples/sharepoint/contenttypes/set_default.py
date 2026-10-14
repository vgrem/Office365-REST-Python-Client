"""
Set the default content type of a list.

Creates a content type, binds it to a document library and makes it the list's
default. The content type and its list binding (and the default) are undone
afterwards unless ``--keep`` is given.

A list's default content type is the first entry of the list root folder's
``UniqueContentTypeOrder``; :meth:`ContentType.set_default` rewrites that order
(``set_default(False)`` moves the content type back to the end).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.contenttypes.creation_information import ContentTypeCreationInformation
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Set the default content type of a list")
    parser.add_argument("--name", default="ZZ ContentType Default", help="Content type name")
    parser.add_argument("--list-title", default="Documents", help="Target list")
    parser.add_argument("--keep", action="store_true", help="Keep the content type and list binding")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    site_ct = ctx.web.content_types.add(ContentTypeCreationInformation(Name=args.name)).execute_query()
    if site_ct.string_id is None:
        raise SystemExit("Failed to create content type")

    target_list = ctx.web.lists.get_by_title(args.list_title)
    list_ct = target_list.content_types.add(
        ContentTypeCreationInformation(Name=args.name, Id=site_ct.string_id)
    ).execute_query()

    list_ct.set_default().execute_query()
    print(f"Content type '{args.name}' is now the default for list: {args.list_title}")

    if not args.keep:
        list_ct.set_default(False).execute_query()
        list_ct.delete_object().execute_query()
        site_ct.delete_object().execute_query()
        print("  (content type and list binding removed after demo)")


if __name__ == "__main__":
    main()
