"""
Export all team memberships to CSV using CollectionCsvWriter.

Each row represents one membership — teams with multiple members
produce multiple rows.

Requires application permission TeamMember.Read.All.

https://learn.microsoft.com/en-us/graph/api/team-list-members
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Export all team memberships to CSV")
    parser.add_argument(
        "--output", default=str(Path(tempfile.gettempdir()) / "teams_membership.csv"), help="output CSV file"
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    with open(args.output, "w", newline="") as f:
        client.teams.get_all().select(["displayName", "members/displayName", "members/email", "members/roles"]).expand(
            ["members"]
        ).to_csv(f).execute_query()

    print(f"Exported to {args.output}")


if __name__ == "__main__":
    main()
