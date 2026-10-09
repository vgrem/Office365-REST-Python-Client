"""
Update a field: title, required, hidden, group, description, form visibility, and indexing.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Update a field definition")
    parser.add_argument("--list-title", default="Documents", help="List containing the field")
    parser.add_argument("field", help="Field internal name or title")
    parser.add_argument("--title", help="New display name")
    parser.add_argument("--required", action="store_true", help="Mark the field as required")
    parser.add_argument("--hidden", action="store_true", help="Hide the field")
    parser.add_argument("--group", help="Field group")
    parser.add_argument("--description", help="Field description")
    parser.add_argument("--hide-in-forms", action="store_true", help="Hide from the new/edit forms (keep display form)")
    parser.add_argument("--index", action="store_true", help="Enable the list index on the field")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    field = ctx.web.lists.get_by_title(args.list_title).fields.get_by_internal_name_or_title(args.field)

    changes = {}
    if args.title:
        changes["Title"] = args.title
    if args.required:
        changes["Required"] = True
    if args.hidden:
        changes["Hidden"] = True
    if args.group:
        changes["Group"] = args.group
    if args.description:
        changes["Description"] = args.description
    if changes:
        field.update_properties(**changes).execute_query()
        print(f"Updated: {', '.join(changes)}")

    if args.hide_in_forms:
        field.set_show_in_new_form(False)
        field.set_show_in_edit_form(False)
        field.set_show_in_display_form(True)
        field.update().execute_query()
        print("Hidden from the new/edit forms")

    if args.index:
        result = field.enable_index().execute_query()
        print(f"Index enabled: {result.value}")


if __name__ == "__main__":
    main()
