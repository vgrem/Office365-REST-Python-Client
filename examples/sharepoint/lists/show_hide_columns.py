"""Show or hide list columns and add/remove them from the default view.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def _set_hidden(target_list, field_name: str, hidden: bool) -> None:
    field = target_list.fields.get_by_internal_name_or_title(field_name)
    field.hidden = hidden
    field.update().execute_query()


def main():
    parser = argparse.ArgumentParser(description="Show or hide list columns")
    parser.add_argument("--list-title", default="Tasks", help="list title")
    parser.add_argument("--column", default="AssignedTo", help="field internal name or title")
    parser.add_argument(
        "--action",
        choices=["hide", "show", "add-to-view", "remove-from-view"],
        default="hide",
        help="operation to apply",
    )
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    target_list = ctx.web.lists.get_by_title(args.list_title)

    if args.action == "hide":
        _set_hidden(target_list, args.column, True)
    elif args.action == "show":
        _set_hidden(target_list, args.column, False)
    elif args.action == "add-to-view":
        target_list.default_view.view_fields.add_view_field(args.column).execute_query()
    else:
        target_list.default_view.view_fields.remove_view_field(args.column).execute_query()
    print(f"{args.action}: '{args.column}' on '{args.list_title}'")


if __name__ == "__main__":
    main()
