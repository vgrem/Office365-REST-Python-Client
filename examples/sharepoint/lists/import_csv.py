"""Import a CSV file into a SharePoint list in bulk.

Parses a local CSV (stdlib) and queues every row via ``queue_records`` — one
item-create is queued per row and runs on ``execute_query()``. The progress hook
fires per imported row (the total is known, so the bar is determinate).

The symmetric counterpart (reading a list back into CSV) is ``export_records.py``.

Sample data is generated locally with faker — swap ``--path`` for a real source.
"""

import argparse
import csv
import os
import tempfile

from faker import Faker
from office365.runtime.converters.csv_reader import read_csv_records
from office365.runtime.progress import progress_bar
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username

CSV_HEADERS = ["Title", "FullName", "Email", "Company", "WorkPhone", "WorkCity", "WorkCountry"]


def make_source_csv(path: str, amount: int) -> None:
    """Generate a sample CSV file locally (stands in for a real data source)."""
    fake = Faker()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for _ in range(amount):
            writer.writerow(
                {
                    "Title": fake.name(),
                    "FullName": fake.name(),
                    "Email": fake.email(),
                    "Company": fake.company(),
                    "WorkPhone": fake.phone_number(),
                    "WorkCity": fake.city(),
                    "WorkCountry": fake.country(),
                }
            )


def main():
    parser = argparse.ArgumentParser(description="Import a CSV file into a SharePoint list")
    parser.add_argument("--path", default=None, help="path to the CSV file (default: generated sample)")
    parser.add_argument("--amount", type=int, default=100, help="rows to generate when --path is not given")
    parser.add_argument("--list-title", default="Contacts_CSV")
    parser.add_argument("--no-progress", action="store_true", help="do not show a tqdm progress bar")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    path = args.path or os.path.join(tempfile.mkdtemp(), "contacts.csv")
    if args.path is None:
        make_source_csv(path, args.amount)

    lst = ctx.web.lists.ensure_list(args.list_title).execute_query()

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        header = csv.DictReader(f).fieldnames
        f.seek(0)
        if header:
            lst.ensure_fields(header)
            ctx.execute_query()
        hook = None if args.no_progress else progress_bar(f"Importing {os.path.basename(path)}")
        lst.queue_records(read_csv_records(f), progress=hook).execute_query()

    print(f"Imported CSV into '{lst.title}'")


if __name__ == "__main__":
    main()
