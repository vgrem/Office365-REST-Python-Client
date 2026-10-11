"""
Cleanup candidates: teams with no channels, and teams with channels but no messages.

An empty team is either a failed provisioning attempt or a workspace that was
never used. Distinguishing "no channels" from "channels but silent" matters:
the first is safe to delete, the second may just be seasonal.

Requires the application permissions ``Team.ReadBasic.All``,
``Channel.ReadBasic.All`` and ``ChannelMessage.Read.All``.

https://learn.microsoft.com/en-us/graph/api/channel-list
https://learn.microsoft.com/en-us/graph/api/channel-list-messages
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _has_messages(channels) -> bool:
    """True as soon as any channel holds at least one message."""
    for channel in channels:
        if channel.messages.top(1).get().execute_query():
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Find teams with no channels or no messages")
    parser.add_argument("--limit", type=int, default=0, help="scan at most N teams (0 = all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = list(client.teams.get_all().select(["id", "displayName"]).execute_query())
    if args.limit:
        teams = teams[: args.limit]
    print(f"Scanning {len(teams)} team(s)…\n")

    empty = silent = 0
    for team in teams:
        channels = team.channels.get().execute_query()
        if not channels:
            empty += 1
            print(f"  NO CHANNELS  {team.display_name}")
        elif not _has_messages(channels):
            silent += 1
            print(f"  NO MESSAGES  {team.display_name}  ({len(channels)} channel(s))")

    print(f"\nSummary: {empty} team(s) without channels, {silent} silent team(s).")


if __name__ == "__main__":
    main()
