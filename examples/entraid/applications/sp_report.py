"""
Audit service principal credentials — passwords and certificates with expiry.

Useful because an app's *service principal* can hold its own credentials that
are separate from the app registration object. Shows every SP that has at least
one credential and flags the ones that are expired or expiring soon.

Usage:

    python sp_report.py
    python sp_report.py --warn-days 60

Requires application permission ``Directory.Read.All``.

Reference:
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

DEFAULT_WARN_DAYS = 30


def _status(cred, warn_days: int) -> str:
    days = cred.days_until_expiry
    if days is None:
        return "  no expiry"
    if cred.is_expired:
        return f"  expired {-days}d ago"
    if days < warn_days:
        return f"  expires in {days}d  <<<"
    return f"  expires in {days}d"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warn-days", type=int, default=DEFAULT_WARN_DAYS)
    args = parser.parse_args()

    client = (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("Directory.Read.All")
    )
    fields = ["displayName", "appId", "passwordCredentials", "keyCredentials"]
    sps = client.service_principals.select(fields).get().execute_query()

    print(f"Service principal credential audit ({len(sps)} SPs)\n")
    for sp in sorted(sps, key=lambda x: x.display_name or ""):
        if not sp.password_credentials and not sp.key_credentials:
            continue
        print(f"\n  {sp.display_name}  (app_id={sp.app_id})")
        for p in sp.password_credentials:
            print(f"    [P] {p.displayName or p.hint or '(unnamed)'}{_status(p, args.warn_days)}")
        for k in sp.key_credentials:
            print(f"    [C] {k.displayName or '(unnamed)'}{_status(k, args.warn_days)}")


if __name__ == "__main__":
    main()
