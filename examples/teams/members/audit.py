"""
Owner hygiene: teams with no owner, and teams with far too many.

A team with no owner is orphaned — nobody can approve membership requests or
change its settings. A team with a dozen owners is the opposite problem: owner
permissions are effectively team-wide admin rights, so least privilege says keep
the list short. Both checks read the same membership list, so they run in one pass.

Requires the application permission ``TeamMember.Read.All`` (and
``Team.ReadBasic.All`` to list the teams).

https://learn.microsoft.com/en-us/graph/api/team-list-members
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

DEFAULT_MAX_OWNERS = 5


def _owners_of(team):
    members = team.members.get().execute_query()
    return members, [m for m in members if "owner" in (m.get_property("roles") or [])]


def main():
    parser = argparse.ArgumentParser(description="Report orphaned and over-owned teams")
    parser.add_argument("--max-owners", type=int, default=DEFAULT_MAX_OWNERS, help="flag teams with more owners")
    parser.add_argument("--limit", type=int, default=0, help="scan at most N teams (0 = all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = list(client.teams.get_all().select(["id", "displayName"]).execute_query())
    if args.limit:
        teams = teams[: args.limit]
    print(f"Checking ownership of {len(teams)} team(s)…\n")

    orphaned, over_owned = [], []
    for team in teams:
        members, owners = _owners_of(team)
        if not owners:
            orphaned.append(team.display_name)
            print(f"  ORPHANED   {team.display_name}")
        elif len(owners) > args.max_owners:
            over_owned.append(team)
            print(f"  {len(owners):>2} owners  {team.display_name}")
            for owner in owners:
                print(f"                 {owner.display_name or '':<35} {owner.get_property('email') or ''}")

    print(f"\nSummary: {len(orphaned)} team(s) without owners, {len(over_owned)} with more than {args.max_owners}.")


if __name__ == "__main__":
    main()
