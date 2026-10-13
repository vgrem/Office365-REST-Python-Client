"""Demonstrates parallel list item import with concurrent batch requests.

Compare with ``import_list.py`` (sequential): passing ``concurrency > 1`` to
``execute_batch`` runs the batch requests on a thread pool, cutting wall time
for large imports. Transient failures (e.g. HTTP 429) are retried, honoring
``Retry-After``; ``success_callback`` runs on the caller thread in completion
order.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse
import time

from faker import Faker
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from tests.settings import client_id, password, team_site_url, tenant, username


def load_source(amount: int) -> list:
    fake = Faker()
    result = []
    for _ in range(amount):
        entry = {
            "Title": fake.name(),
            "FullName": fake.name(),
            "Email": fake.email(),
            "Company": fake.company(),
            "WorkPhone": fake.phone_number(),
            "WorkAddress": fake.street_address(),
            "WorkCity": fake.city(),
            "WorkZip": fake.postcode(),
            "WorkCountry": fake.country(),
            # "WebPage": {"Url": fake.url()},
        }
        result.append(entry)

    return result


def run_import(source_data: list, target_list: List, items_per_batch: int, concurrency: int) -> None:
    ctx = target_list.context
    for item in source_data:
        target_list.add_item(item)

    total = len(source_data)
    added = {"count": 0}
    started_at = time.monotonic()

    def _print_progress(return_types) -> None:
        added["count"] += len([t for t in return_types if isinstance(t, ListItem)])
        print(f"[{time.strftime('%H:%M:%S')}] {added['count']}/{total} items added")

    print(f"Importing {total} items (batch={items_per_batch}, concurrency={concurrency})...")
    ctx.execute_batch(
        items_per_batch=items_per_batch,
        concurrency=concurrency,
        success_callback=_print_progress,
    )
    print(f"Done in {time.monotonic() - started_at:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Import list items with concurrent batch requests")
    parser.add_argument("--list-title", default="Contacts_Large", help="target list title")
    parser.add_argument("--amount", type=int, default=1000, help="number of items to generate")
    parser.add_argument("--items-per-batch", type=int, default=50, help="items per batch request")
    parser.add_argument("--concurrency", type=int, default=5, help="number of concurrent batch requests")
    args = parser.parse_args()

    client = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant,
        client_id=client_id,
        username=username,
        password=password,
    )
    contacts_list = client.web.lists.get_by_title(args.list_title).get().execute_query()
    source = load_source(args.amount)
    contacts_list.ensure_fields(list(source[0].keys()))
    client.execute_query()
    run_import(source, contacts_list, args.items_per_batch, args.concurrency)


if __name__ == "__main__":
    main()
