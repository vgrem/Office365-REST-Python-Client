"""
List every license (subscription SKU) the tenant owns, with its service plans.

The fastest way to answer "which Microsoft 365 products / add-ons do we have?"
— for example whether Microsoft 365 Backup, Copilot, or an E5 seat pool is
present. Every SKU shows seat usage and, with ``--plans``, the individual
service plans it unlocks.

    python list_skus.py
    python list_skus.py --plans
    python list_skus.py --filter backup

Requires application permission ``Organization.Read.All``.

https://learn.microsoft.com/en-us/graph/api/subscribedsku-list

Note: the configuration is read-only. To *manage* licenses use
``report.py``, ``assign.py`` and ``modify_service_plans.py``.
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="List tenant licenses (subscribed SKUs)")
    parser.add_argument("--filter", help="Only show SKUs whose part number or a service plan contains this text")
    parser.add_argument("--plans", action="store_true", help="List every service plan of each SKU")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    skus = client.subscribed_skus.get().execute_query()

    needle = args.filter.upper() if args.filter else None
    shown = 0
    for sku in skus:
        part_number = sku.sku_part_number or "?"
        plan_names = [plan.servicePlanName or "" for plan in sku.service_plans]
        haystack = " ".join([part_number, *plan_names]).upper()
        if needle is not None and needle not in haystack:
            continue

        shown += 1
        enabled = sku.prepaid_units.enabled or 0
        consumed = sku.consumed_units or 0
        print(part_number)
        print(
            f"  seats:  {consumed}/{enabled} used   "
            f"status: {sku.capability_status or '?'}   applies to: {sku.applies_to or '?'}"
        )
        print(f"  skuId:  {sku.sku_id}")
        if args.plans:
            for plan_name in plan_names:
                print(f"    - {plan_name}")
        else:
            print(f"  service plans: {len(plan_names)}  (pass --plans to list them)")
        print()

    if needle is not None and shown == 0:
        print(f"No SKU or service plan matched {args.filter!r}.")
    else:
        suffix = f" matching {args.filter!r}" if needle is not None else ""
        print(f"Licenses{suffix}: {shown}")


if __name__ == "__main__":
    main()
