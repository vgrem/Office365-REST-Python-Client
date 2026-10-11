"""
Lifecycle report: archived teams and recently deleted (restorable) groups.

Archiving freezes a team in read-only mode — the usual way to retire a project
without losing its history. Deleting a Microsoft 365 group is different: it is a
soft delete, and the group stays restorable for 30 days. This script shows both
states side by side.

Requires the application permissions ``Team.ReadBasic.All`` and
``Directory.Read.All``.

https://learn.microsoft.com/en-us/graph/api/team-list
https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-list
https://learn.microsoft.com/en-us/graph/api/team-archive
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

RESTORE_WINDOW_DAYS = 30


def _days_since(dt: datetime | None) -> int | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt).days


def main():
    parser = argparse.ArgumentParser(description="Report archived and recently deleted teams")
    parser.add_argument("--limit", type=int, default=0, help="list at most N teams per section (0 = all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = list(client.teams.get_all().select(["id", "displayName", "isArchived"]).execute_query())
    archived = [team for team in teams if team.is_archived]

    print(f"Teams: {len(teams) - len(archived)} active, {len(archived)} archived")
    for team in archived[: args.limit or None]:
        print(f"  ARCHIVED  {team.display_name}")

    deleted = list(client.directory.deleted_teams.get().select(["id", "displayName", "deletedDateTime"]).execute_query())
    print(f"\nRecently deleted (restorable for {RESTORE_WINDOW_DAYS} days): {len(deleted)}")
    for group in deleted[: args.limit or None]:
        days_ago = _days_since(group.deleted_datetime)
        if days_ago is None:
            print(f"  {group.get_property('displayName')}")
        else:
            print(
                f"  {group.get_property('displayName')}  "
                f"(deleted {days_ago}d ago, {max(0, RESTORE_WINDOW_DAYS - days_ago)}d left)"
            )

    print("\nUse governance/restore.py to restore or permanently delete a group.")


if __name__ == "__main__":
    main()
