"""
List an app's certificates (key credentials) with their validity status.

Shows, for one app, every registered certificate together with its thumbprint
(``customKeyIdentifier``) and whether it is expired, not yet valid, expiring
soon or valid. Handy when mapping a certificate back to the app that owns it.

Usage:

    python list_certificates.py                    # this app
    python list_certificates.py --app-id <guid>
    python list_certificates.py --warn-days 60

Requires application permission ``Directory.Read.All``.

Reference:
    https://learn.microsoft.com/en-us/graph/api/resources/keycredential
"""

from __future__ import annotations

import argparse

from office365.directory.key_credential import KeyCredential
from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

DEFAULT_WARN_DAYS = 30


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("Directory.Read.All")
    )


def _status(cred: KeyCredential, warn_days: int) -> str:
    if cred.is_expired:
        return "EXPIRED"
    days = cred.days_until_expiry
    if days is None:
        return "NO EXPIRY"
    if days < warn_days:
        return "EXPIRING SOON"
    return "VALID"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to inspect")
    parser.add_argument("--warn-days", type=int, default=DEFAULT_WARN_DAYS)
    args = parser.parse_args()

    client = _client()
    app = client.applications.get_by_app_id(args.app_id).get().execute_query()

    certs = app.key_credentials
    print(f"{app.display_name}: {len(certs)} certificate(s)\n")
    for cred in certs:
        name = cred.displayName or "<unnamed>"
        end = cred.endDateTime.date() if cred.endDateTime else "-"
        print(f"  {name:<24} {_status(cred, args.warn_days):<14} expires {end}  {cred.customKeyIdentifier or ''}")


if __name__ == "__main__":
    main()
