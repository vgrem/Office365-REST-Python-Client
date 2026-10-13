"""
Create a lookup field and optionally a dependent (secondary) lookup.

A lookup references a field from another list; a dependent lookup is
linked to the primary lookup and shows an additional source field.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Create a lookup field (optionally with a dependent lookup)")
    parser.add_argument("--list-title", default="Documents", help="Target list")
    parser.add_argument("--source-list", default="Tasks", help="Source list the lookup references")
    parser.add_argument("--field", default="RelatedTask", help="Lookup field display name")
    parser.add_argument("--show-field", default="Title", help="Source field shown by the lookup")
    parser.add_argument("--dependent", help="Display name of a dependent lookup field to add")
    parser.add_argument("--keep", action="store_true", help="Keep created fields (default: delete after demo)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    target_list = ctx.web.lists.get_by_title(args.list_title)
    source_list = ctx.web.lists.get_by_title(args.source_list)

    lookup = target_list.fields.add_lookup_field(
        title=args.field,
        lookup_list=source_list,
        lookup_field_name=args.show_field,
    ).execute_query()
    print(f"Lookup field created: {lookup.internal_name}  (id: {lookup.id})")

    dependent = None
    if args.dependent:
        if lookup.id is None:
            raise SystemExit("Lookup field id is not available")
        dependent = target_list.fields.add_dependent_lookup_field(
            args.dependent, lookup.id, args.show_field
        ).execute_query()
        print(f"Dependent lookup created: {dependent.internal_name}")

    if not args.keep:
        # A primary lookup cannot be removed while dependent lookups reference it.
        if dependent is not None:
            dependent.delete_object().execute_query()
        lookup.delete_object().execute_query()
        print("  (fields removed after demo)")


if __name__ == "__main__":
    main()
