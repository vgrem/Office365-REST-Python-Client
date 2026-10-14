"""
Add an existing site-level content type to a list.

The content type must already be available on the site (a site content type or
one pushed from the content type hub). The demo is a no-op when the content
type is already bound to the list, and removes the binding afterwards unless
``--keep`` is given.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Add an existing site content type to a list")
    parser.add_argument("--ct-id", required=True, help="Content type id (e.g. 0x0120)")
    parser.add_argument("--list-title", default="Documents", help="Target list")
    parser.add_argument("--keep", action="store_true", help="Keep the content type bound to the list")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    target_list = ctx.web.lists.get_by_title(args.list_title)
    existing = target_list.content_types.get().execute_query()

    if any((ct.string_id or "").startswith(args.ct_id) for ct in existing):
        print(f"Content type '{args.ct_id}' is already available on list: {args.list_title}")
        return

    added = target_list.content_types.add_available_content_type(args.ct_id).execute_query()
    print(f"Content type '{added.name or args.ct_id}' added to list: {args.list_title}")

    if not args.keep:
        added.delete_object().execute_query()
        print("  (list binding removed after demo)")


if __name__ == "__main__":
    main()
