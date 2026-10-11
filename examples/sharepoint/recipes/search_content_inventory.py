"""
Build a content inventory across SharePoint from a search query.

Pages through the SharePoint Search REST API, writes every hit to CSV, and prints
a summary grouped by site and file type — plus how many documents have not
changed within ``--stale-days``. Useful for cleanup, migration scoping, and
"what lives where" questions across the tenant.

    python search_content_inventory.py --output inventory.csv
    python search_content_inventory.py --query "filetype:docx AND ProjectStage:Review" --stale-days 180

Requires ``Sites.Read.All`` (search returns only what the calling identity can see).

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

from __future__ import annotations

import argparse
import csv
import re
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

COLUMNS = ["Path", "Title", "Author", "LastModifiedTime", "FileExtension", "Size"]
TOP_N = 10


def parse_timestamp(value: datetime | str | None) -> datetime | None:
    """Return an aware UTC timestamp from a search ``LastModifiedTime`` value.

    The SDK deserializes ``LastModifiedTime`` to ``datetime`` but a raw string is
    also accepted; naive values are assumed to be UTC so they compare cleanly.
    """
    if isinstance(value, datetime):
        parsed = value
    elif value:
        text = str(value).strip().replace("Z", "+00:00")
        text = re.sub(r"(\.\d{6})\d+", r"\1", text)  # fromisoformat accepts at most 6 fractional digits
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def site_from_url(url: str) -> str:
    """Reduce a document URL to its site collection path (``/sites/team``)."""
    vendor, _, remainder = urlparse(url).path.lstrip("/").partition("/")
    site, _, _ = remainder.partition("/")
    if site and vendor in ("sites", "personal", "teams"):
        return f"/{vendor}/{site}"
    return "/"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a SharePoint content inventory from a search query")
    parser.add_argument("--query", default="IsDocument:1", help="KQL query")
    parser.add_argument(
        "--output", default=str(Path(tempfile.gettempdir()) / "content_inventory.csv"), help="output CSV path"
    )
    parser.add_argument("--limit", type=int, default=1000, help="maximum documents to collect")
    parser.add_argument("--page-size", type=int, default=100, help="results per search page")
    parser.add_argument("--stale-days", type=int, default=365, help="flag documents older than this many days")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    rows: list[dict] = []
    start_row = 0
    while len(rows) < args.limit:
        page = ctx.search.query(
            query_text=args.query,
            start_row=start_row,
            row_limit=min(args.page_size, args.limit - len(rows)),
            select_properties=COLUMNS,
        ).execute_query()
        hits = page.value.PrimaryQueryResult.RelevantResults.Table.Rows
        if not hits:
            break
        for hit in hits:
            cells = hit.Cells
            rows.append({col: cells.get(col, "") for col in COLUMNS})
        start_row += len(hits)
        print(f"  fetched {len(rows)} row(s)...")

    if not rows:
        print("No results.")
        return

    now = datetime.now(timezone.utc)
    stale_after = timedelta(days=args.stale_days)
    by_site: Counter = Counter()
    by_ext: Counter = Counter()
    stale = 0

    output_rows = []
    for hit in rows:
        site = site_from_url(hit["Path"])
        modified = parse_timestamp(hit["LastModifiedTime"])
        is_stale = "yes" if modified and (now - modified) > stale_after else "no"
        output_rows.append({**hit, "Site": site, "Stale": is_stale})

        by_site[site] += 1
        by_ext[(hit["FileExtension"] or "(none)").lower()] += 1
        stale += is_stale == "yes"

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[*COLUMNS, "Site", "Stale"])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nInventory: {len(rows)} document(s) -> {args.output}")
    print(f"Stale (>{args.stale_days} days): {stale}\n")

    print("By site:")
    for name, count in by_site.most_common(TOP_N):
        print(f"  {count:5d}  {name}")
    print("\nBy type:")
    for ext, count in by_ext.most_common(TOP_N):
        print(f"  {count:5d}  {ext}")


if __name__ == "__main__":
    main()
