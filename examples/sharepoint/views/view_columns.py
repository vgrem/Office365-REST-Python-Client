"""
Add, remove, and reorder columns in a view.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Manage view columns")
    parser.add_argument("--view", required=True, help="View title")
    parser.add_argument("--list-title", default="Documents", help="List or library title")
    parser.add_argument("--add", help="Field internal name or title to add")
    parser.add_argument("--remove", help="Field internal name or title to remove")
    parser.add_argument("--move", help="Field internal name or title to move")
    parser.add_argument("--to", type=int, help="Zero-based position for --move")
    args = parser.parse_args()

    if not any((args.add, args.remove, args.move)):
        raise SystemExit("Provide --add, --remove, or --move")
    if args.move and args.to is None:
        raise SystemExit("--move requires --to")

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    view = ctx.web.lists.get_by_title(args.list_title).views.get_by_title(args.view)
    fields = view.view_fields

    if args.add:
        fields.add_view_field(args.add).execute_query()
        print(f"Added column: {args.add}")
    if args.remove:
        fields.remove_view_field(args.remove).execute_query()
        print(f"Removed column: {args.remove}")
    if args.move:
        assert args.to is not None
        fields.move_view_field_to(args.move, args.to).execute_query()
        print(f"Moved column '{args.move}' to position {args.to}")

    columns = view.view_fields.get().execute_query()
    print(f"View columns ({len(columns)}): {list(columns)}")


if __name__ == "__main__":
    main()
