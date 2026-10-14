"""
Find which lists use a given content type.

Useful before deleting or changing a content type — it shows every list
the content type is associated with (including hidden lists).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Find lists that use a content type")
    parser.add_argument("--name", help="Content type name")
    parser.add_argument("--id", dest="string_id", help="Content type string id (e.g. 0x0120...)")
    parser.add_argument("--list-title", help="Only scan this list (default: all lists)")
    parser.add_argument("--include-hidden", action="store_true", help="Also scan hidden/system lists")
    args = parser.parse_args()

    if not args.name and not args.string_id:
        raise SystemExit("Provide --name or --id")

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    ct = (
        ctx.web.content_types.find_by_name(args.name, required=True)
        if args.name
        else ctx.web.content_types.get_by_id(args.string_id)
    )
    ctx.load(ct, ["Name", "StringId"]).execute_query()
    print(f"Scanning lists for '{ct.name}' ({ct.string_id})...\n")

    if args.list_title:
        lists = [ctx.web.lists.get_by_title(args.list_title).get().execute_query()]
    else:
        lists = ctx.web.lists.get().execute_query()

    # A list stores a list-scoped copy of a site content type: its id is the site
    # content type's id with the list's GUID appended (e.g. ``0x0101`` ->
    # ``0x01010026fe...``). So a list uses the content type when its id *starts
    # with* the site id, not when the two are exactly equal.
    site_id = ct.string_id or ""
    found = []
    for lst in lists:
        if not args.include_hidden and lst.hidden:
            continue
        list_cts = lst.content_types.get().execute_query()
        matches = [c.name for c in list_cts if (c.string_id or "").startswith(site_id)]
        marker = " (hidden)" if lst.hidden else ""
        if matches:
            found.append(lst.title)
            print(f"  {lst.title:40s} {matches}{marker}")

    print(f"\n{len(found)} list(s) use '{ct.name}'")
    if not found:
        print("  (none — safe to delete if no list items depend on it)")


if __name__ == "__main__":
    main()
