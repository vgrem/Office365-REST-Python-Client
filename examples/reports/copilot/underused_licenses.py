"""
Find users assigned a Copilot license who haven't signed in recently.

Cross-references Copilot SKUs with per-user license assignments and last sign-in
activity to flag underused (or unused) Copilot licenses — the input for a reclaim
or adoption campaign.

Reading ``signInActivity`` needs ``AuditLog.Read.All``; if the app lacks it the
script prints the hint and exits without failing.

    python underused_licenses.py
    python underused_licenses.py --days 60 --limit 100

Requires application permissions ``Organization.Read.All``, ``User.Read.All``
and ``AuditLog.Read.All``.

https://learn.microsoft.com/en-us/graph/api/user-list
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant

COPILOT_KEYWORDS = ("COPILOT",)


def _as_datetime(value) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Find underused Copilot licenses")
    parser.add_argument("--days", type=int, default=30, help="No-sign-in threshold in days (default: 30)")
    parser.add_argument("--limit", type=int, default=100, help="Maximum users to list (default: 100)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    sku_ids = {
        sku.sku_id
        for sku in client.subscribed_skus.get().execute_query()
        if any(keyword in (sku.sku_part_number or "").upper() for keyword in COPILOT_KEYWORDS)
    }
    if not sku_ids:
        print("No Copilot SKUs found in the tenant — nothing to check.")
        return

    try:
        users = list(
            client.users.select(["displayName", "userPrincipalName", "assignedLicenses", "signInActivity"])
            .get()
            .execute_query()
        )
    except ClientRequestException as exc:
        if exc.response.status_code in (401, 403):
            print("Could not read sign-in activity; grant the 'AuditLog.Read.All' application permission.")
            return
        raise

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    underused = []
    for user in users:
        licensed = [lic for lic in (user.assigned_licenses or []) if lic.skuId in sku_ids]
        if not licensed:
            continue
        last_sign_in = _as_datetime(user.sign_in_activity.lastSignInDateTime)
        if last_sign_in is None or last_sign_in < cutoff:
            underused.append((user, last_sign_in))

    print(f"Copilot users with no sign-in for {args.days}+ days: {len(underused)}\n")
    for user, last_sign_in in underused[: args.limit]:
        print(f"  {user.user_principal_name:45s}  last sign-in: {last_sign_in or 'never'}")


if __name__ == "__main__":
    main()
