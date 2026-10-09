"""
Set the default content type for a list.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.contenttypes.creation_information import ContentTypeCreationInformation
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Set the default content type for a list")
    parser.add_argument("--name", required=True, help="Content type name")
    parser.add_argument("--list-title", default="Documents", help="Target list")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    site_ct = ctx.web.content_types.add(
        ContentTypeCreationInformation(Name=args.name, Description="For Contoso projects")
    ).execute_query()
    if site_ct.string_id is None:
        raise SystemExit("Failed to create content type")

    target_list = ctx.web.lists.get_by_title(args.list_title)
    list_ct = target_list.content_types.add(
        ContentTypeCreationInformation(Name=args.name, Id=site_ct.string_id)
    ).execute_query()

    # The default flag lives on the list's content type binding
    list_ct.set_default(True).update().execute_query()
    print(f"Default content type set: {list_ct.name} on '{args.list_title}'")


if __name__ == "__main__":
    main()
