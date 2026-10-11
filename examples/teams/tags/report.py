"""
Report: all tags across all teams with member count, and teams without tags.

Requires application permission ``TeamworkTag.Read.All`` and
``Team.ReadBasic.All``.

https://learn.microsoft.com/en-us/graph/api/teamworktag-list
"""

import argparse
from typing import Optional

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _resolve_teams(client: GraphClient, team_id: Optional[str]):
    if team_id:
        team = client.teams[team_id].get().execute_query()
        return [team] if team else []
    return list(client.teams.get_all().execute_query() or [])


def main():
    parser = argparse.ArgumentParser(description="Report tags across teams")
    parser.add_argument("--team", default=None, help="only inspect this team id (otherwise all teams)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = _resolve_teams(client, args.team)

    tagged = set()
    for team in teams:
        try:
            tags = team.tags.get().execute_query()
        except ClientRequestException as ex:
            if ex.code != "Forbidden":
                raise
            print(f"✗ Tags are not readable with this app ({ex.code})")
            print("  Grant TeamworkTag.Read.All (application) or the")
            print("  TeamworkTag.Read.Group resource-specific consent, then re-run.")
            return
        for tag in tags:
            tagged.add(team.display_name)
            print(f"  [{team.display_name}]  {tag.display_name}  ({tag.member_count} members)")

    untagged = [t.display_name for t in teams if t.display_name and t.display_name not in tagged]
    if untagged:
        print(f"\nTeams without tags ({len(untagged)}): {', '.join(untagged)}")


if __name__ == "__main__":
    main()
