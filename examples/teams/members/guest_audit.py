"""
Guest access report: which teams have external users, and who they are.

External guests have ``#EXT#`` in their user principal name, which is a quick
way to spot them without resolving every member through the directory. Useful
before an access review, or to check that guest settings are actually enforced.

Requires the application permission ``TeamMember.Read.All`` (and
``Team.ReadBasic.All`` to list the teams).

https://learn.microsoft.com/en-us/graph/api/team-list-members
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Report teams that contain guest users")
    parser.add_argument("--limit", type=int, default=0, help="scan at most N teams (0 = all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = list(client.teams.get_all().select(["id", "displayName"]).execute_query())
    if args.limit:
        teams = teams[: args.limit]
    print(f"Scanning {len(teams)} team(s) for guest access…\n")

    affected = total_guests = 0
    for team in teams:
        guests = [m for m in team.members.get().execute_query() if "#EXT#" in (m.get_property("email") or "")]
        if not guests:
            continue
        affected += 1
        total_guests += len(guests)
        print(f"  {team.display_name}  ({len(guests)} guest(s))")
        for guest in guests:
            roles = guest.get_property("roles") or ["member"]
            print(f"      {guest.display_name or '':<35} {guest.get_property('email') or '':<40} {', '.join(roles)}")

    print(f"\nSummary: {total_guests} guest(s) across {affected} of {len(teams)} team(s).")


if __name__ == "__main__":
    main()
