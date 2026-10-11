"""
Report on tabs (pinned apps) across all Microsoft Teams.

Walks teams -> channels -> tabs and lists which apps are pinned,
so you can see how apps are surfaced in the UI.

Requires delegated or application permissions:
    Team.ReadBasic.All     List all teams
    Channel.ReadBasic.All  List channels
    Tab.Read.All           Read tabs

https://learn.microsoft.com/en-us/graph/api/team-list-channels
https://learn.microsoft.com/en-us/graph/api/channel-list-tabs
"""

import argparse
from typing import Optional

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _resolve_teams(client: GraphClient, team_id: Optional[str]):
    if team_id:
        team = client.teams[team_id].get().execute_query()
        return [team] if team else []
    return list(client.teams.get_all().execute_query() or [])


def main():
    parser = argparse.ArgumentParser(description="Tabs (pinned apps) across teams")
    parser.add_argument("--team", default=None, help="only inspect this team id (otherwise all teams)")
    parser.add_argument("--max-teams", type=int, default=0, help="limit the number of teams scanned (default: all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = _resolve_teams(client, args.team)
    if args.max_teams:
        teams = teams[: args.max_teams]

    total_tabs = 0
    for team in teams:
        try:
            channels = team.channels.get().execute_query()
        except Exception:
            continue
        for channel in channels:
            try:
                tabs = channel.tabs.expand(["teamsApp"]).get().execute_query()
            except Exception:
                continue
            for tab in tabs:
                app = tab.teams_app
                app_name = app.display_name if app else "?"
                entity = tab.configuration.entityId if tab.configuration else None
                total_tabs += 1
                print(
                    f"  {team.display_name:30s} / {channel.display_name:30s}  "
                    f"{tab.properties.get('displayName', '?') or '?':30s} app={app_name}  entityId={entity or '-'}"
                )

    print(f"\nTotal tabs: {total_tabs}")


if __name__ == "__main__":
    main()
