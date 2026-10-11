"""
Report on apps installed across all Microsoft Teams, with adoption metrics.

Detects shadow IT (unexpected sideloaded apps) and tracks app adoption:
which apps are installed in how many teams, and which catalog apps are
not installed anywhere.

Requires delegated or application permissions:
    Team.ReadBasic.All              List all teams
    TeamsAppInstallation.Read.All   Read installed apps per team
    AppCatalog.Read.All             (optional) compare against the app catalog

https://learn.microsoft.com/en-us/graph/api/teamsappinstallation-list
"""

import argparse
from collections import Counter
from typing import Optional

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _app_name(installation) -> str:
    definition = installation.teams_app_definition
    return definition.properties.get("displayName", "(unknown)")


def _app_id(installation) -> str:
    definition = installation.teams_app_definition
    return definition.properties.get("teamsAppId", installation.properties.get("id", "?"))


def _resolve_teams(client: GraphClient, team_id: Optional[str]):
    if team_id:
        team = client.teams[team_id].get().execute_query()
        return [team] if team else []
    return list(client.teams.get_all().execute_query() or [])


def main():
    parser = argparse.ArgumentParser(description="Installed apps report and adoption summary")
    parser.add_argument("--team", default=None, help="only inspect this team id (otherwise all teams)")
    parser.add_argument("--catalog", action="store_true", help="compare adoption against the tenant app catalog")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = _resolve_teams(client, args.team)

    installs: Counter = Counter()  # app name -> number of teams it is installed in
    by_team = []  # (team display name, [app names])
    for team in teams:
        try:
            apps = team.installed_apps.expand(["teamsAppDefinition"]).get().execute_query()
        except ClientRequestException:
            continue
        names = [_app_name(a) for a in apps]
        for name in names:
            installs[name] += 1
        by_team.append((team.display_name, names))
        print(f"[{team.display_name}]  {len(apps)} app(s)")

    print(f"\nAdoption summary ({len(teams)} teams):")
    for name, count in installs.most_common():
        print(f"  {count:3d} teams  {name}")

    if args.catalog:
        try:
            catalog = client.app_catalogs.teams_apps.expand(["appDefinitions"]).get().execute_query()
        except ClientRequestException as ex:
            if ex.code != "Forbidden":
                raise
            print("\n✗ The app catalog is not readable (Forbidden); skipping the catalogue comparison.")
            print("  Grant AppCatalog.Read.All to list apps that are not installed anywhere.")
            return
        catalog_names = {
            app.display_name
            for app in catalog
            if app.display_name and any(d.properties.get("publishingState") == "published" for d in app.app_definitions)
        }
        unused = sorted(catalog_names - set(installs))
        print(f"\nCatalog apps not installed in any team ({len(unused)}):")
        for name in unused:
            print(f"  {name}")


if __name__ == "__main__":
    main()
