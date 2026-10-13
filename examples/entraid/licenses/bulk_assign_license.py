"""
Bulk assign Microsoft 365 licenses to users from a CSV file.

Reads a CSV with user principal names and SKU IDs, then assigns
licenses in batch. Tracks success/failure per user for reporting.

Inspired by Assign-LicensesViaCSV.PS1 from Office 365 for IT Pros.

Required delegated permissions:
    User.ReadWrite.All          Update user license assignments
    Organization.Read.All       List available SKUs
    User.Read.All               Read user directory info

https://learn.microsoft.com/en-us/graph/api/user-assignlicense
"""

from __future__ import annotations

import csv
from io import StringIO

from office365.directory.licenses.assigned_license import AssignedLicense
from office365.graph_client import GraphClient
from office365.runtime.types.collections import StringCollection
from tests.settings import client_id, client_secret, tenant

CSV_DATA = """user_principal_name,sku_id,disabled_plans
user1@contoso.com,contoso:SPE_E3,
user2@contoso.com,contoso:SPE_E5,SWAY
user3@contoso.com,contoso:SPE_E3,TEAMS1
"""


def resolve_sku_id(client: GraphClient, sku_part: str) -> str | None:
    """Resolve a SKU display name or partial ID to a full GUID."""
    skus = client.subscribed_skus.get().execute_query()
    for sku in skus:
        name = sku.sku_part_number or ""
        sid = sku.sku_id or ""
        if sku_part.lower() in name.lower() or sku_part.lower() in sid.lower():
            return sid
    return None


def resolve_user(client: GraphClient, upn: str) -> str | None:
    """Resolve a user principal name to a user ID."""
    try:
        user = client.users.filter(f"userPrincipalName eq '{upn}'").get().execute_query()
        if user:
            return user[0].id
    except Exception:
        pass
    return None


def bulk_assign_licenses(csv_content: str) -> list[dict]:
    """Assign licenses to users based on CSV content.

    Args:
        csv_content: CSV string with columns: user_principal_name, sku_id, disabled_plans.

    Returns:
        List of result dicts with status per user.
    """
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    reader = csv.DictReader(StringIO(csv_content))
    results = []

    for row in reader:
        upn = row["user_principal_name"].strip()
        sku_input = row["sku_id"].strip()
        disabled = [p.strip() for p in row.get("disabled_plans", "").split(",") if p.strip()]

        # Resolve SKU
        sku_id = resolve_sku_id(client, sku_input)
        if not sku_id:
            results.append({"user": upn, "status": "skipped", "error": f"SKU '{sku_input}' not found"})
            continue

        # Resolve user
        user_id = resolve_user(client, upn)
        if not user_id:
            results.append({"user": upn, "status": "skipped", "error": "User not found"})
            continue

        # Assign license
        try:
            disabled_ids = []
            if disabled:
                # Look up service plan IDs for disabled plans
                for sku in client.subscribed_skus.get().execute_query():
                    if sku.sku_id == sku_id:
                        for sp in sku.service_plans:
                            if sp.servicePlanName in disabled:
                                disabled_ids.append(sp.servicePlanId or "")
                        break

            user = client.users[user_id]
            user.assign_license(
                add_licenses=[AssignedLicense(skuId=sku_id, disabledPlans=StringCollection(disabled_ids))],
                remove_licenses=[],
            ).execute_query()

            results.append({"user": upn, "status": "success", "sku": sku_input})
        except Exception as e:
            results.append({"user": upn, "status": "failed", "error": str(e)})

    return results


def main():
    print("Bulk license assignment from CSV\n")

    # Replace CSV_DATA with your own file in production:
    # with open("licenses.csv") as f:
    #     csv_content = f.read()
    csv_content = CSV_DATA

    results = bulk_assign_licenses(csv_content)

    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] == "skipped"]

    print(f"Total:  {len(results)}")
    print(f"Success: {len(success)}")
    print(f"Failed:  {len(failed)}")
    print(f"Skipped: {len(skipped)}\n")

    for r in failed + skipped:
        error = r.get("error", "Unknown")
        print(f"  ✗ {r['user']}: {error}")

    if success:
        print(f"\n✓ {len(success)} licenses assigned successfully.")


if __name__ == "__main__":
    main()
