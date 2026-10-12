"""
Consolidated credential report — every app's passwords and certificates with
their expiry status.

This is the starting point for credential hygiene: it shows, in one view, which
app registrations have client secrets or certificates, when they expire, and
which ones are already past their end date (the usual cause of the
``AADSTS7000222`` error).

Usage:

    python credentials_report.py                  # every app, warn below 30 days
    python credentials_report.py --warn-days 60
    python credentials_report.py --expired-only   # only already-expired credentials

Requires application permission ``Directory.Read.All`` (delegated
``Application.Read.All`` also works).

Reference:
    https://learn.microsoft.com/en-us/graph/api/resources/application
    https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

DEFAULT_WARN_DAYS = 30


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("Directory.Read.All")
    )


def _status(cred, warn_days: int) -> str:
    days = cred.days_until_expiry
    if days is None:
        return "no expiry set"
    if cred.is_expired:
        return f"EXPIRED {-days}d ago"
    if days < warn_days:
        return f"expires in {days}d <<<"
    return f"expires in {days}d"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warn-days", type=int, default=DEFAULT_WARN_DAYS, help="warn below this many days")
    parser.add_argument("--expired-only", action="store_true", help="only show apps with expired credentials")
    args = parser.parse_args()

    client = _client()
    listed = 0

    for app in client.applications.get_all().execute_query():
        creds = [(f"[P] {p.displayName or p.hint or '(unnamed)'}", p) for p in (app.password_credentials or [])]
        creds += [(f"[C] {k.displayName or k.keyId or '(unnamed)'}", k) for k in (app.key_credentials or [])]
        if not creds or (args.expired_only and not any(c.is_expired for _, c in creds)):
            continue

        print(f"\n{app.display_name}  (app_id={app.app_id})")
        for label, cred in creds:
            print(f"  {label:36s}  {_status(cred, args.warn_days)}")
            listed += 1

    print(f"\n{listed} credential(s) listed.")


if __name__ == "__main__":
    main()
