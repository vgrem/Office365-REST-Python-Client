"""
Tenant-wide Teams inventory: for every team, its membership breakdown.

The console counterpart of ``export/inventory.py``: same list, but printed as a
report instead of written to a file. Use it to eyeball adoption — how many
teams are private, how many are archived, who has the most guests.

Requires the application permissions ``Team.ReadBasic.All`` and
``TeamMember.Read.All``.

https://learn.microsoft.com/en-us/graph/api/team-list
https://learn.microsoft.com/en-us/graph/api/team-list-members
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _counts(team):
    members = team.members.get().execute_query()
    owners = sum(1 for m in members if "owner" in (m.get_property("roles") or []))
    guests = sum(1 for m in members if "#EXT#" in (m.get_property("email") or ""))
    return len(members), owners, guests


def main():
    parser = argparse.ArgumentParser(description="Print a tenant-wide Teams inventory")
    parser.add_argument("--limit", type=int, default=0, help="inspect at most N teams (0 = all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = list(client.teams.get_all().select(["id", "displayName", "visibility", "isArchived"]).execute_query())
    if args.limit:
        teams = teams[: args.limit]
    print(f"Inspecting {len(teams)} team(s)…\n")

    total_members = total_guests = archived = 0
    for team in teams:
        members, owners, guests = _counts(team)
        total_members += members
        total_guests += guests
        archived += 1 if team.is_archived else 0
        state = "archived" if team.is_archived else "active"
        visibility = team.visibility.value if team.visibility else "?"
        print(
            f"  {team.display_name or '':<40} {visibility:<9} {state:<9}"
            f" {members:>4} members ({owners} owners, {guests} guests)"
        )

    print(
        f"\nTotals: {len(teams)} team(s), {archived} archived, {total_members} membership(s), {total_guests} guest(s)."
    )


if __name__ == "__main__":
    main()
