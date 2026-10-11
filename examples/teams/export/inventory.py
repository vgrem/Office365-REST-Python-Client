"""
Export a tenant-wide Teams inventory to CSV and JSON.

For every team: identity, visibility, description, archive state, and
membership counts (owners/members/guests).

    python export/inventory.py --output /tmp/teams_export

Requires application permissions Team.ReadBasic.All, TeamMember.Read.All,
Directory.Read.All.
"""

import argparse
import csv
import json
import os
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Export the tenant Teams inventory")
    parser.add_argument(
        "--output",
        default=str(Path(tempfile.gettempdir()) / "teams_export"),
        help="output directory for teams.csv / teams.json",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    print("Exporting Teams inventory…", flush=True)

    rows = []
    teams = (
        client.teams.get_all().select(["id", "displayName", "visibility", "mailNickname", "description"]).execute_query()
    )
    for team in teams:
        members = team.members.get().execute_query()
        owners = sum(1 for m in members if "owner" in (m.properties.get("roles") or []))
        guests = sum(1 for m in members if "#EXT#" in (m.properties.get("email") or ""))
        rows.append(
            {
                "id": team.id,
                "displayName": team.display_name,
                "visibility": team.visibility.value if team.visibility else None,
                "mailNickname": team.properties.get("mailNickname"),
                "description": team.description,
                "isArchived": team.is_archived,
                "owners": owners,
                "members": len(members),
                "guests": guests,
            }
        )

    os.makedirs(args.output, exist_ok=True)
    csv_path = os.path.join(args.output, "teams.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["id"])
        writer.writeheader()
        writer.writerows(rows)

    json_path = os.path.join(args.output, "teams.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print(f"Exported {len(rows)} teams -> {csv_path}, {json_path}")


if __name__ == "__main__":
    main()
