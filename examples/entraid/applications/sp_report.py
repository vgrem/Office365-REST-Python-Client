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
        creds = list(sp.password_credentials or []) + list(sp.key_credentials or [])
        if not creds:
            continue
        print(f"\n  {sp.display_name}  (app_id={sp.app_id})")
        for cred in creds:
            # ``cred.kind`` is "Password"/"Certificate"; ``expiry_status`` is a printable label.
            print(f"    [{cred.kind}] {cred.expiry_status(args.warn_days)}")


if __name__ == "__main__":
    main()
