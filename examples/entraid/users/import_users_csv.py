"""
Import users from a CSV file via the streaming data pipeline (``from_csv``).

Each row becomes a user-create request; the file is streamed in chunks, so
memory stays bounded no matter how many rows it holds. Failures (for example a
UPN that already exists) are collected instead of aborting the run.

The sample file lives in ``examples/data/users.csv``; pass ``--path`` to import
your own. ``--domain`` sets the UPN domain for the ``userName`` column.

The record-at-a-time counterpart is ``import.py``.

Requires delegated permission ``User.ReadWrite.All`` (and ``pandas``, installed
via ``office365-rest-python-client[pandas]``).

https://learn.microsoft.com/en-us/graph/api/user-post-users
"""

from __future__ import annotations

import argparse
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.converters.dataframe import records_from_dataframe
from office365.runtime.progress import progress_bar
from tests.settings import client_id, password, tenant, username

SAMPLE_CSV = Path(__file__).resolve().parents[2] / "data" / "users.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk-provision users from a CSV file")
    parser.add_argument("--path", default=str(SAMPLE_CSV), help="CSV file (default: examples/data/users.csv)")
    parser.add_argument("--domain", default=tenant, help="UPN domain appended to each `userName` value")
    parser.add_argument("--chunk", type=int, default=50, help="rows per commit")
    parser.add_argument("--apply", action="store_true", help="create the users (default: preview only)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    def to_records(chunk) -> list[dict]:
        """Turn the CSV columns into user records (build the UPN, enable the account)."""
        records = records_from_dataframe(chunk)
        for record in records:
            record["userPrincipalName"] = f"{record.pop('userName')}@{args.domain}"
            record["mailNickname"] = record["userPrincipalName"].split("@")[0]
            record["accountEnabled"] = True
        return records

    result = client.users.from_csv(
        args.path,
        chunksize=args.chunk,
        to_records=to_records,
        mapping={"password": "passwordProfile/password"},
        on_error="collect",
        dry_run=not args.apply,
        progress=progress_bar("Importing users"),
    ).execute_query()

    print(result.value.summary())
    for failure in result.checkpoint.failures:
        print(f"  {failure.get('error', failure)}")


if __name__ == "__main__":
    main()
