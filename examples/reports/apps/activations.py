"""
Office activations — installed vs assigned licenses.

Two Office licensing reports:

* **activation counts** — installs that were activated, broken down by product
  and platform (Windows, Mac, Android, iOS);
* **activations user counts** — how many users were assigned a product vs how
  many actually activated it.

The gap between *assigned* and *activated* is the reclaimable-license signal.

    python activations.py

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getoffice365activationcounts
https://learn.microsoft.com/en-us/graph/api/reportroot-getoffice365activationsusercounts
"""

from __future__ import annotations

import argparse
import csv
import io

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _rows(result) -> list[dict]:
    """Decode a report result into CSV rows (the CSV carries a UTF-8 BOM)."""
    value = result.value
    text = value.decode("utf-8-sig") if isinstance(value, bytes) else (value.content or b"").decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def _int(value) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def _platform_rows(result) -> None:
    rows = _rows(result)
    if not rows:
        print("Activation counts: no data (the tenant may have no Office activations)")
        return
    row = rows[-1]
    platforms = [c for c in row if c not in ("Report Refresh Date", "Product Type")]
    print(f"Activation counts ({row.get('Report Refresh Date')}):")
    print(f"  {'Product':20s}  " + "  ".join(f"{p:>10s}" for p in platforms))
    for entry in rows:
        cells = "  ".join(f"{_int(entry.get(p)):>10,}" for p in platforms)
        print(f"  {entry.get('Product Type') or '?':20s}  {cells}")


def _user_rows(result) -> None:
    rows = _rows(result)
    if not rows:
        print("\nActivations user counts: no data")
        return
    print("\nAssigned vs activated users:")
    for entry in rows:
        assigned = _int(entry.get("Assigned"))
        activated = _int(entry.get("Activated"))
        gap = assigned - activated
        print(
            f"  {entry.get('Product Type') or '?':20s}  activated {activated:>6,} / assigned {assigned:>6,}"
            f"   gap {gap:>6,}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Office activations and assigned licenses")
    parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    _platform_rows(client.reports.get_office365_activation_counts().execute_query())
    _user_rows(client.reports.get_office365_activations_user_counts().execute_query())


if __name__ == "__main__":
    main()
