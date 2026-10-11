"""
Install, uninstall, and inspect Teams apps in a team.

Covers the common app lifecycle operations:
  search    Find a catalog app by name (to get its id)
  list      List apps installed in a team
  install   Install a catalog app into a team
  uninstall Remove an app installation from a team

Requires delegated or application permissions ``AppCatalog.ReadWrite.All``,
``TeamsAppInstallation.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/teamsappinstallation-add
https://learn.microsoft.com/en-us/graph/api/teamsappinstallation-delete
"""

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.teams.team import Team
from tests.settings import client_id, client_secret, tenant

TEAMS_APP_URL = "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/{app_id}"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _get_team(client: GraphClient, team_id: str) -> Team:
    return client.teams[team_id].get().execute_query()


def cmd_search(client: GraphClient, args: argparse.Namespace) -> None:
    apps = client.app_catalogs.teams_apps.filter(f"contains(displayName,'{args.query}')").get().execute_query()
    print(f"Catalog matches ({len(apps)}):")
    for app in apps:
        print(f"  {app.id:50s} {app.display_name}")


def cmd_list(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    installations = team.installed_apps.expand(["teamsAppDefinition"]).get().execute_query()
    print(f"Installed apps in '{team.display_name}' ({len(installations)}):")
    for inst in installations:
        name = inst.teams_app_definition.properties.get("displayName", "(unknown)")
        version = inst.teams_app_definition.properties.get("version", "?")
        print(f"  {inst.id:50s} {name:35s} version={version}")


def cmd_install(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    bind = TEAMS_APP_URL.format(app_id=args.app_id)
    installation = team.installed_apps.add(**{"teamsApp@odata.bind": bind}).execute_query()
    print(f"Installed app into '{team.display_name}': {installation.id}")


def cmd_uninstall(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    installation = team.installed_apps[args.installation_id]
    installation.delete_object().execute_query()
    print(f"Uninstalled app from '{team.display_name}': {args.installation_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Teams app installations")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search", help="find a catalog app by name")
    p.add_argument("query", help="substring of the app display name")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("list", help="list apps installed in a team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("install", help="install a catalog app into a team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--app", dest="app_id", required=True, help="catalog app id (see 'search')")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("uninstall", help="remove an app installation from a team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--installation-id", required=True, help="app installation id (see 'list')")
    p.set_defaults(func=cmd_uninstall)

    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.func(_client(), args)
    except ClientRequestException as ex:
        if ex.code != "Forbidden":
            raise
        print(f"✗ Access denied ({ex.code})")
        print("  Required scopes: AppCatalog.Read.All / AppCatalog.ReadWrite.All (search),")
        print("  TeamsAppInstallation.ReadWriteForTeam.All (install/uninstall),")
        print("  TeamsAppInstallation.Read.All (list). Run as a delegated user if the app is not granted these roles.")


if __name__ == "__main__":
    main()
