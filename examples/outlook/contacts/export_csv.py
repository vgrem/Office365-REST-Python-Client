"""
Export personal contacts to CSV via the data pipeline (``to_csv``).

Columns follow ``.select()``; the deferred export writes after
``execute_query()`` completes the load. Useful for CRM sync or migration.

Requires delegated permission ``Contacts.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-contacts
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

COLUMNS = ["displayName", "givenName", "surname", "companyName", "jobTitle", "mobilePhone", "businessPhones"]


def main():
    parser = argparse.ArgumentParser(description="Export contacts to CSV via the data pipeline")
    parser.add_argument(
        "--output", default=str(Path(tempfile.gettempdir()) / "contacts_export.csv"), help="output CSV file"
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    contacts = client.me.contacts.get_all().select(COLUMNS)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        contacts.to_csv(f).execute_query()

    print(f"Exported contacts to {args.output}")


if __name__ == "__main__":
    main()
