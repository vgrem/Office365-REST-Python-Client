"""
Check whether the tenant is licensed for Microsoft 365 Backup Storage.

Microsoft 365 Backup Storage is a **paid add-on**: the ``backupRestore`` endpoint
is only usable on a tenant that owns the corresponding add-on SKU. This script
lists the subscribed SKUs and highlights any match, so a failed backup example
can be diagnosed without guesswork.

Requires ``Organization.Read.All`` or ``Directory.Read.All`` (both are carried by
the examples' app registration).

https://learn.microsoft.com/en-us/graph/api/subscribedsku-list
"""

from __future__ import annotations

import argparse

from office365.directory.licenses.subscribed_sku import SubscribedSku
from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the tenant's Microsoft 365 Backup license")
    parser.add_argument("--keyword", default="backup", help="SKU part-number keyword to look for (default: backup)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    skus = client.subscribed_skus.get().execute_query()

    keyword = args.keyword.lower()

    def is_match(sku: SubscribedSku) -> bool:
        return bool(sku.sku_part_number) and keyword in sku.sku_part_number.lower()

    print("Subscribed SKUs:")
    for sku in skus:
        marker = "  <-- match" if is_match(sku) else ""
        print(f"  {sku.sku_part_number:<34} {sku.consumed_units}/{sku.prepaid_units.enabled} seats{marker}")

    matches = [sku for sku in skus if is_match(sku)]
    if matches:
        print(f"\nTenant is licensed for '{args.keyword}' ({len(matches)} SKU(s)).")
    else:
        print(f"\nNo subscribed SKU matches '{args.keyword}'.")
        print("Microsoft 365 Backup Storage is a paid add-on; without that SKU the")
        print("backupRestore endpoint stays unavailable (see README.md -> 'Licensing').")


if __name__ == "__main__":
    main()
