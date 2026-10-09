"""An end-to-end data pipeline: extract -> transform -> load between two lists.

Showcases the collection as a first-class pipeline citizen:

- **Extract** — ``get_all(progress=...)`` streams every row with a progress hook
  (the total is unknown for server-driven paging, so the bar is indeterminate).
- **Transform** — ``to_records()`` projects loaded items into plain dicts;
  filter / normalize them with plain Python (no pandas required).
- **Load** — ``from_records()`` queues an item-create per record into the target
  list; the progress hook fires per row as each create completes (total known).

The records form is the neutral interchange between every format adapter
(CSV / JSON / NDJSON / Excel / DataFrame), so the same three steps apply to any
of them.
"""

import argparse

from office365.runtime.progress import progress_bar
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username


def transform(records: list) -> list:
    """Example transform: keep rows with a country, normalize email casing."""
    transformed = []
    for record in records:
        if not record.get("WorkCountry"):
            continue
        if record.get("Email"):
            record["Email"] = record["Email"].lower()
        transformed.append(record)
    return transformed


def main():
    parser = argparse.ArgumentParser(description="ETL between two SharePoint lists")
    parser.add_argument("--source-list", default="Contacts_Large")
    parser.add_argument("--target-list", default="Contacts_Filtered")
    parser.add_argument(
        "--select", default="Title,FullName,Email,Company,WorkCountry", help="comma-separated fields to extract"
    )
    parser.add_argument("--no-progress", action="store_true", help="do not show tqdm progress bars")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    # -- Extract: stream the source list (indeterminate read progress) --
    read_hook = None if args.no_progress else progress_bar(f"Extracting {args.source_list}")
    items = (
        ctx.web.lists.get_by_title(args.source_list)
        .items.get_all(progress=read_hook)
        .select(args.select.split(","))
        .execute_query()
    )
    records = items.to_records()
    print(f"Extracted {len(records)} records")

    # -- Transform: filter / normalize in plain Python --
    cleaned = transform(records)
    print(f"Transformed -> {len(cleaned)} records (dropped {len(records) - len(cleaned)})")

    # -- Load: queue an item-create per record into the target list --
    target = ctx.web.lists.ensure_list(args.target_list).execute_query()
    target.ensure_fields(args.select.split(","))
    ctx.execute_query()
    write_hook = None if args.no_progress else progress_bar(f"Loading into {args.target_list}")
    target.items.queue_records(cleaned, progress=write_hook).execute_query()
    print(f"Loaded {len(cleaned)} records into '{target.title}'")


if __name__ == "__main__":
    main()
