"""
List Backup Storage browse sessions and browse their protected locations.

A browse session is a time-boxed, read-only view of a restore point. The
``browse`` action walks a location (a site, a document library or a folder) and
returns the items it contains, which is how a granular restore is planned. The
browse is a no-op unless ``--apply`` is given.

Requires delegated or application permission ``BackupRestore-Control.Read.All``.
On an unlicensed tenant the call is denied and a short license hint is printed.

https://learn.microsoft.com/en-us/graph/api/browsesessionbase-browse
"""

from __future__ import annotations

import argparse
from typing import Sequence

from office365.backuprestore.browse_session_base import BrowseSessionBase
from office365.backuprestore.restoresessions.browsable_resource_type import (
    BrowsableResourceType,
)
from office365.backuprestore.restoresessions.browse_query_order import BrowseQueryOrder
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _print_sessions(label: str, sessions: Sequence[BrowseSessionBase]) -> None:
    print(f"{label} ({len(sessions)}):")
    for session in sessions:
        print(f"  {session.id}  status={session.status}  restorePoint={session.restore_point_id}")
        print(
            f"      size={session.backup_size_in_bytes}  valid until={session.expiration_date_time}",
        )


def _run(client: GraphClient, args: argparse.Namespace) -> None:
    backup = client.solutions.backup_restore
    _print_sessions("SharePoint browse sessions", list(backup.sharepoint_browse_sessions.get().execute_query()))
    _print_sessions(
        "OneDrive for Business browse sessions",
        list(backup.onedrive_for_business_browse_sessions.get().execute_query()),
    )

    if not args.browse:
        return

    if args.workload == "onedrive":
        collection = backup.onedrive_for_business_browse_sessions
    else:
        collection = backup.sharepoint_browse_sessions
    session = collection[args.browse]

    if not args.apply:
        print(
            f"\nDry run. Would POST browse for {args.workload} session {args.browse} "
            f"(item key {args.item_key!r}, type {args.resource_type})."
        )
        return

    result = session.browse(
        args.item_key,
        BrowsableResourceType[args.resource_type],
        order_by=BrowseQueryOrder.nameAsc,
    ).execute_query()

    print(f"\nItems in {args.item_key or '(session root)'} ({len(result.value)}):")
    for item in result.value:
        print(f"  {item.name}  type={item.type}  size={item.sizeInBytes}  key={item.itemKey}")


def main() -> None:
    parser = argparse.ArgumentParser(description="List and browse Backup Storage sessions")
    parser.add_argument("--browse", metavar="SESSION_ID", help="Browse the contents of this browse session")
    parser.add_argument("--item-key", default="", help="Item key to browse (default: session root)")
    parser.add_argument(
        "--resource-type",
        default="site",
        choices=[member.name for member in BrowsableResourceType],
        help="Kind of item to browse (default: site)",
    )
    parser.add_argument("--workload", default="sharepoint", choices=["sharepoint", "onedrive"])
    parser.add_argument("--apply", action="store_true", help="Actually run the browse")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    try:
        _run(client, args)
    except ClientRequestException as err:
        print("Microsoft 365 Backup Storage is not available on this tenant.")
        print("It is a paid add-on and must be enabled; see README.md -> 'Licensing'.")
        print(f"\nServer response: {err}")


if __name__ == "__main__":
    main()
