"""
Bulk-provision teams from a CSV file (onboarding).

Each row creates a team with ``client.teams.create_and_wait(...)`` and waits for
provisioning before moving on:

    name,description,template
    Finance,"Budgeting and reporting",standard
    Marketing,"Campaign workspace",standard

    python export/provision.py --file teams.csv --dry-run

Requires the application permission ``Group.ReadWrite.All`` (plus
``Team.Create`` when creating from a template). For concurrent provisioning of
a large batch, see ``../patterns/async/provision_teams_async.py``.
"""

import argparse
import csv
import sys

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant, user_principal

DEFAULT_TEMPLATE = "standard"


def main():
    parser = argparse.ArgumentParser(description="Bulk-create teams from a CSV file")
    parser.add_argument("--file", required=True, help="CSV with name,description?,template? columns")
    parser.add_argument("--limit", type=int, default=0, help="create at most N teams (0 = all)")
    parser.add_argument(
        "--owner",
        default=user_principal,
        help="UPN or id of the owning user (required in application context)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print what would be created, do nothing")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("No rows in the CSV file")

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    created = errors = 0
    for row in rows[: args.limit or None]:
        name = row["name"].strip()
        description = (row.get("description") or "").strip() or None
        template = (row.get("template") or DEFAULT_TEMPLATE).strip()

        if args.dry_run:
            print(f"would create: {name} (template={template})")
            continue

        try:
            team = client.teams.create_and_wait(name, description, template, owners=[args.owner]).execute_query()
        except ClientRequestException as e:
            errors += 1
            print(f"  failed: {name} — {e}")
            continue

        created += 1
        print(f"  created: {team.display_name} ({team.id})")

    print(f"\nCreated {created} team(s), {errors} error(s)")


if __name__ == "__main__":
    main()
