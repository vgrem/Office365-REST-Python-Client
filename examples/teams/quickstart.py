"""
The smallest Teams script: connect and list the teams in the tenant.

Every other script in this folder is a variation on this idea — address a team,
read or change something on it, then clean up after yourself. Pass ``--create``
to also provision a throwaway team, which is a good look at the one part of the
Teams API that is *asynchronous*: creating a team returns a
``teamsAsyncOperation`` and the library's ``create_and_wait`` polls it until
provisioning finishes, then deletes the team again.

Requires the application permission ``Team.ReadBasic.All`` (plus
``Group.ReadWrite.All`` and ``Team.Create`` when ``--create`` is used).

https://learn.microsoft.com/en-us/graph/api/team-list
https://learn.microsoft.com/en-us/graph/api/team-post
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant, user_principal


def main():
    parser = argparse.ArgumentParser(description="List the tenant's teams")
    parser.add_argument("--limit", type=int, default=20, help="how many teams to print")
    parser.add_argument("--create", action="store_true", help="also create and delete a throwaway team")
    parser.add_argument(
        "--owner",
        default=user_principal,
        help="UPN or id of the user who owns the created team (required in application context)",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = list(client.teams.get_all().select(["id", "displayName", "visibility", "isArchived"]).execute_query())

    print(f"{len(teams)} team(s):")
    for team in teams[: args.limit]:
        state = "archived" if team.is_archived else "active"
        visibility = team.visibility.value if team.visibility else "?"
        print(f"  {team.display_name or '':<45} {visibility:<10} {state}  {team.id}")

    if not args.create:
        return

    # Team creation is a long-running operation: `create_and_wait` chains the
    # POST, the `teamsAsyncOperation` poll, and a final GET. Application-only
    # clients must name an owner, otherwise Teams rejects the request.
    team = client.teams.create_and_wait(
        "SDK quickstart", "Temporary team — safe to delete", owners=[args.owner]
    ).execute_query()
    print(f"\nCreated '{team.display_name}' ({team.id})")
    team.delete_object().execute_query()
    print("Deleted it again.")


if __name__ == "__main__":
    main()
