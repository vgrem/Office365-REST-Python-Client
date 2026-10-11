"""
Apple VPP tokens: volume-purchase licensing and its sync/expiry health.

Apple's Volume Purchase Program (VPP) tokens are how an organisation buys App
Store apps and books in bulk and assigns them to devices or users. Tokens must
be re-imported before they expire; this script flags stale syncs and tokens that
expire within 30 days.

    python licensing.py

Requires delegated permission ``DeviceManagementApps.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-apps-vpptokens-list
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def as_utc(value: datetime | None) -> datetime | None:
    """Treat a naive Graph timestamp as UTC so comparisons are timezone-safe."""
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def main() -> None:
    parser = argparse.ArgumentParser(description="Report on Apple VPP token health")
    parser.add_argument("--expiring-days", type=int, default=30, help="Flag tokens expiring within N days")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        tokens = list(client.device_app_management.vpp_tokens.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementApps.Read.All and re-run.")
        return

    now = datetime.now(timezone.utc)
    expiring_before = now + timedelta(days=args.expiring_days)
    stale_before = now - timedelta(days=7)

    print(f"Apple VPP tokens ({len(tokens)}):\n")
    for token in tokens:
        flags = []
        if (as_utc(token.last_sync_date_time) or now) < stale_before:
            flags.append("[STALE]")
        if (as_utc(token.expiration_date_time) or expiring_before) < expiring_before:
            flags.append("[EXPIRING]")
        print(f"  {token.organization_name or '(unnamed)':35s} [{token.state or '?'}] {' '.join(flags)}".rstrip())
        print(f"    Apple ID:  {token.apple_id or '?'}  Account: {token.vpp_token_account_type or '?'}")
        print(f"    Last sync: {token.last_sync_date_time or 'never'}  ({token.last_sync_status or '?'})")
        print(f"    Expires:   {token.expiration_date_time or '?'}")
        print()


if __name__ == "__main__":
    main()
