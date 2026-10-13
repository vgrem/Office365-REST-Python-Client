"""
Bulk-create users from generated profiles via the batch data pipeline.

Records are generated locally (faker) and queued on the collection; a single
``execute_batch`` commits them in server-side batches, so N creates cost a
handful of round trips. The CSV-driven counterpart is ``import_users_csv.py``.

Requires delegated permission ``User.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/user-post-users
"""

from __future__ import annotations

import argparse

from faker import Faker
from office365.graph_client import GraphClient
from office365.runtime.progress import progress_bar
from tests.settings import client_id, password, tenant, username


def make_record(fake: Faker) -> dict:
    """Build one user-create record from faker-generated values."""
    user_name = fake.user_name()
    return {
        "userPrincipalName": f"{user_name}@{tenant}",
        "mailNickname": user_name,
        "displayName": fake.name(),
        "department": fake.job(),
        "officeLocation": fake.street_address(),
        "city": fake.city(),
        "country": fake.country(),
        "accountEnabled": True,
        "passwordProfile": {"password": "P@ssw0rd-" + fake.password(length=8)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk-create generated users in batched requests")
    parser.add_argument("--count", type=int, default=25, help="number of users to create")
    args = parser.parse_args()

    fake = Faker()
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    client.users.queue_records([make_record(fake) for _ in range(args.count)], progress=progress_bar("Creating users"))
    client.execute_batch(20)
    print(f"Created {args.count} users")


if __name__ == "__main__":
    main()
