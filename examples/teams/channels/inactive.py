"""
Find channels that have gone quiet, across every team.

The per-channel companion of ``governance/inactive.py`` (which judges the team
as a whole). Channel-level reporting is useful when a team is alive in one place
and abandoned everywhere else.

Requires the application permissions ``Team.ReadBasic.All``,
``Channel.ReadBasic.All`` and ``ChannelMessage.Read.All``.

https://learn.microsoft.com/en-us/graph/api/channel-list
https://learn.microsoft.com/en-us/graph/api/channel-list-messages
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _last_message(channel) -> datetime | None:
    try:
        messages = channel.messages.top(1).order_by("createdDateTime desc").get().execute_query()
    except ClientRequestException:
        return None
    return messages[0].created_datetime if messages else None


def main():
    parser = argparse.ArgumentParser(description="Find channels with no recent messages")
    parser.add_argument("--days", type=int, default=90, help="inactivity threshold in days")
    parser.add_argument("--limit", type=int, default=0, help="scan at most N teams (0 = all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    teams = list(client.teams.get_all().select(["id", "displayName"]).execute_query())
    if args.limit:
        teams = teams[: args.limit]
    print(f"Scanning channels in {len(teams)} team(s)…\n")

    inactive = []
    for team in teams:
        for channel in team.channels.get().execute_query():
            last = _last_message(channel)
            if last is None or last < cutoff:
                inactive.append((team.display_name, channel.display_name, last))

    print(f"Inactive channels ({args.days}+ days): {len(inactive)}")
    for team_name, channel_name, last in inactive:
        seen = last.strftime("%Y-%m-%d") if last else "never"
        print(f"  {team_name}  ›  {channel_name}  (last message: {seen})")


if __name__ == "__main__":
    main()
