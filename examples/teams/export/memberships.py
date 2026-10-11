"""
Export every team membership to CSV — one row per member.

Walks all teams and writes ``team,displayName,email,roles``; a team with no
members yields a single row with empty member fields. Handy for ownership
reviews, guest audits, and offline membership diffing.

    python export/memberships.py --output /tmp/teams_membership.csv

Requires application permission TeamMember.Read.All.

https://learn.microsoft.com/en-us/graph/api/team-list-members
"""

import argparse
import csv
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Export all team memberships to CSV")
    parser.add_argument(
        "--output",
        default=str(Path(tempfile.gettempdir()) / "teams_membership.csv"),
        help="output CSV file",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = client.teams.get_all().select(["id", "displayName"]).execute_query()

    rows = 0
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["team", "displayName", "email", "roles"])
        for team in teams:
            members = team.members.get().execute_query()
            if not members:
                writer.writerow([team.display_name, "", "", ""])
                continue
            for member in members:
                writer.writerow(
                    [
                        team.display_name,
                        member.display_name or "",
                        member.properties.get("email") or "",
                        "; ".join(member.roles) if member.roles else "",
                    ]
                )
                rows += 1

    print(f"Exported {rows} membership(s) from {len(teams)} team(s) to {args.output}")


if __name__ == "__main__":
    main()
