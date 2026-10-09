"""Demonstrates parallel list item import with concurrent batch requests.

Compare with ``import_list.py`` (sequential): passing ``concurrency > 1`` to
``execute_batch`` runs the batch requests on a thread pool, cutting wall time
for large imports. Transient failures (e.g. HTTP 429) are retried, honoring
``Retry-After``; ``success_callback`` runs on the caller thread in completion
order.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import time

from faker import Faker
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from tests.settings import client_id, password, team_site_url, tenant, username

AMOUNT = 1000
ITEMS_PER_BATCH = 50
CONCURRENCY = 5
LIST_TITLE = "Contacts_Large"


def load_source(amount: int = AMOUNT) -> list:
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


def run_import(source_data: list, target_list: List) -> None:
    ctx = target_list.context
    for item in source_data:
        target_list.add_item(item)

    total = len(source_data)
    added = {"count": 0}
    started_at = time.monotonic()

    def _print_progress(return_types) -> None:
        added["count"] += len([t for t in return_types if isinstance(t, ListItem)])
        print(f"[{time.strftime('%H:%M:%S')}] {added['count']}/{total} items added")

    print(f"Importing {total} items into '{LIST_TITLE}' (batch={ITEMS_PER_BATCH}, concurrency={CONCURRENCY})...")
    ctx.execute_batch(
        items_per_batch=ITEMS_PER_BATCH,
        concurrency=CONCURRENCY,
        success_callback=_print_progress,
    )
    print(f"Done in {time.monotonic() - started_at:.2f}s")


if __name__ == "__main__":
    client = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant,
        client_id=client_id,
        username=username,
        password=password,
    )
    contacts_list = client.web.lists.get_by_title(LIST_TITLE).get().execute_query()
    source = load_source()
    contacts_list.ensure_fields(list(source[0].keys()))
    client.execute_query()
    run_import(source, contacts_list)
