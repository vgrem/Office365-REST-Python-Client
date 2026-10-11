"""
List recently deleted Microsoft 365 groups and restore — or permanently delete — one.

Mirrors the admin center "Deleted groups" page: Microsoft 365 groups are
soft-deleted and restorable (along with their associated data) for 30 days,
after which they are permanently removed. Other group types are deleted
permanently immediately.

Requires delegated permission ``Group.ReadWrite.All`` or ``Directory.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-list
https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-restore
https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-delete
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

RESTORE_WINDOW_DAYS = 30


def _deleted_at(item) -> datetime | None:
    dt = item.deleted_datetime
    if not dt:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def main():
    parser = argparse.ArgumentParser(description="List, restore, or permanently delete deleted Microsoft 365 groups")
    parser.add_argument("--teams-only", action="store_true", help="show only deleted groups with an associated team")
    parser.add_argument("--restore", help="id of a deleted group to restore (default: list only)")
    parser.add_argument("--permanent", help="id of a deleted group to permanently delete")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    deleted = (
        (client.directory.deleted_teams if args.teams_only else client.directory.deleted_groups)
        .select(["id", "displayName", "deletedDateTime", "resourceProvisioningOptions"])
        .get()
        .execute_query()
    )

    print(f"Deleted Microsoft 365 groups ({len(deleted)}):")
    for group in deleted:
        name = group.get_property("displayName") or "?"
        deleted_dt = _deleted_at(group)
        if deleted_dt is None:
            print(f"  {group.id}  {name}")
            continue
        days_ago = (datetime.now(timezone.utc) - deleted_dt).days
        remaining = max(0, RESTORE_WINDOW_DAYS - days_ago)
        label = f"deleted {days_ago}d ago, {remaining}d to restore"
        print(f"  {group.id}  {name}  ({label})")

    if args.restore:
        target = next((g for g in deleted if g.id == args.restore), None)
        if target is None:
            raise SystemExit(f"Deleted group '{args.restore}' not found")
        target.restore().execute_query()
        print(f"Restored: {target.get_property('displayName') or args.restore}")

    if args.permanent:
        target = next((g for g in deleted if g.id == args.permanent), None)
        if target is None:
            raise SystemExit(f"Deleted group '{args.permanent}' not found")
        target.delete_object().execute_query()
        print(f"Permanently deleted: {target.get_property('displayName') or args.permanent}")


if __name__ == "__main__":
    main()
