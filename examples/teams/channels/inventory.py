"""
Cross-team channel inventory and audit.

Lists every channel across teams with its membership type, archive
status, and email, and summarizes how channels are structured.

Private and shared channels extend the collaboration surface (guests,
external members), so this flags them for security review.

Requires delegated or application permissions:
    Team.ReadBasic.All     List all teams
    Channel.ReadBasic.All  List channels

https://learn.microsoft.com/en-us/graph/api/team-list-channels
"""

import argparse
from collections import Counter
from typing import Optional

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.prefer import prefer_include_unknown_enum_members
from tests.settings import client_id, client_secret, tenant


def _resolve_teams(client: GraphClient, team_id: Optional[str]):
    if team_id:
        team = client.teams[team_id].get().execute_query()
        return [team] if team else []
    return list(client.teams.get_all().execute_query() or [])


def main():
    parser = argparse.ArgumentParser(description="Cross-team channel inventory and audit")
    parser.add_argument("--team", default=None, help="only inspect this team id (otherwise all teams)")
    parser.add_argument("--max-teams", type=int, default=0, help="limit the number of teams scanned (default: all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = _resolve_teams(client, args.team)
    if args.max_teams:
        teams = teams[: args.max_teams]

    summary: Counter = Counter()
    extended = 0
    for team in teams:
        try:
            qry = team.channels.get()
            # `shared` is an evolvable enum member: ask Graph to return it instead of unknownFutureValue
            client.before_execute(prefer_include_unknown_enum_members)
            channels = qry.execute_query()
        except ClientRequestException:
            continue
        print(f"[{team.display_name}]  {len(channels)} channel(s)")
        for ch in channels:
            membership = ch.membership_type.value
            membership = "unknown" if membership == "2" else membership
            archived = ch.is_archived or False
            summary[membership] += 1
            if membership != "standard":
                extended += 1
            print(
                f"  {ch.display_name or '(unnamed)':30s} type={membership:9s} "
                f"archived={'yes' if archived else 'no ':3s} email={ch.email or '-'}"
            )

    print("\nSummary:")
    for membership, count in summary.most_common():
        print(f"  {membership:9s}: {count}")
    print(f"  private/shared (extended surface): {extended}")


if __name__ == "__main__":
    main()
