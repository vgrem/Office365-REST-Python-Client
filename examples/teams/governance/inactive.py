"""
Prune inactive teams — report, archive, or delete teams idle for too long.

A team is considered inactive when it has no messages for at least ``--days``
(no messages at all counts as inactive). Destructive actions (archive/delete)
run as a dry run unless ``--apply`` is passed.

    python governance/inactive.py                          # report candidates (>= 90 days)
    python governance/inactive.py --days 90 --action archive --apply
    python governance/inactive.py --days 365 --action delete --apply --team "Old team"

Requires the application permissions ``Team.ReadBasic.All``,
``ChannelMessage.Read.All`` and ``Group.ReadWrite.All``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _last_activity(team) -> datetime | None:
    """Newest message date across the team's channels (None when no messages)."""
    latest = None
    for channel in team.channels.get().execute_query():
        try:
            msgs = channel.messages.top(1).order_by("createdDateTime desc").get().execute_query()
        except ClientRequestException:
            continue
        if not msgs:
            continue
        created = msgs[0].created_datetime
        if created and (latest is None or created > latest):
            latest = created
    return latest


def main():
    parser = argparse.ArgumentParser(description="Report, archive, or delete inactive teams")
    parser.add_argument("--days", type=int, default=90, help="inactivity threshold in days")
    parser.add_argument("--action", choices=["report", "archive", "delete"], default="delete")
    parser.add_argument("--apply", action="store_true", help="actually run archive/delete (dry run by default)")
    parser.add_argument("--team", help="restrict to one team by display name")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    candidates = []
    for team in client.teams.get_all().execute_query():
        if team.is_archived or (args.team and team.display_name != args.team):
            continue
        last = _last_activity(team)
        if last is None or last < cutoff:
            days = (datetime.now(timezone.utc) - last).days if last else None
            candidates.append((team, days))

    print(f"{len(candidates)} inactive team(s) (no activity in {args.days} days)")
    for team, days in sorted(candidates, key=lambda item: item[1] or -1, reverse=True):
        inactive = "no messages" if days is None else f"{days}d"
        visibility = team.visibility.value if team.visibility else "?"
        print(f"  {team.display_name}  ({visibility})  inactive: {inactive}")

    if args.action == "report":
        return

    if not args.apply:
        print(f"\nDry run — pass --apply to {args.action} {len(candidates)} team(s).")
        return

    for team, _days in candidates:
        if args.action == "archive":
            team.archive().execute_query()
        else:
            team.delete_object().execute_query_retry()
        print(f"  {args.action}d: {team.display_name}")


if __name__ == "__main__":
    main()
