"""
App protection (MAM) policies: data-loss rules that travel with the app.

Mobile Application Management (MAM) protects corporate data *inside* an app
(block copy/paste, require a PIN, wipe app data) without managing the whole
device — the core of "bring your own device". This script lists the policies
and the app registrations they apply to.

    python app_protection.py              # list MAM policies
    python app_protection.py --details    # + each policy's description/version

Requires delegated permission ``DeviceManagementApps.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-mam-managedapppolicy-list
https://learn.microsoft.com/en-us/graph/api/intune-mam-managedappregistration-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="List app protection (MAM) policies")
    parser.add_argument("--details", action="store_true", help="Also show each policy's description and version")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    try:
        policies = list(client.device_app_management.managed_app_policies.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementApps.Read.All and re-run.")
        return

    print(f"App protection policies ({len(policies)}):")
    for policy in policies:
        print(f"  {policy.display_name or '(unnamed)':45s} created: {policy.created_date_time or '?'}")
        if args.details:
            print(f"      {policy.description or '(no description)'}  v{policy.version or '?'}")

    try:
        registrations = list(client.device_app_management.managed_app_registrations.get_all().execute_query())
        print(f"\nManaged app registrations ({len(registrations)}):")
        for registration in registrations:
            print(f"  {registration.entity_type_name or '?'}")
    except ClientRequestException as exc:
        print(f"\n[skipped] registrations: {exc.code}")


if __name__ == "__main__":
    main()
