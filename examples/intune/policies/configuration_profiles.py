"""
Configuration profiles: the settings delivered to devices.

Configuration profiles (``deviceConfigurations``) are how Intune pushes settings
— Wi-Fi, VPN, certificates, restrictions — to devices. This script lists them
and, with ``--details``, the number of assignments and the deployment status.

    python configuration_profiles.py             # list profiles
    python configuration_profiles.py --details   # + assignment/status rollup

Requires delegated permission ``DeviceManagementConfiguration.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-deviceconfig-deviceconfiguration-list
https://learn.microsoft.com/en-us/graph/api/intune-deviceconfig-deviceconfigurationassignment-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="List Intune configuration profiles")
    parser.add_argument("--details", action="store_true", help="Also show assignments and device status")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        profiles = list(client.device_management.device_configurations.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementConfiguration.Read.All and re-run.")
        return

    print(f"Configuration profiles ({len(profiles)}):")
    if not profiles:
        return

    for profile in profiles:
        created = profile.created_date_time or "?"
        print(f"  {profile.display_name or '(unnamed)':45s} v{profile.version or '?'}  created: {created}")
        if not args.details:
            continue
        assignments = profile.assignments.get().execute_query()
        print(f"    Assigned to {len(assignments)} target(s)")
        overview = profile.device_status_overview.get().execute_query()
        print(
            f"    Devices: {overview.success_count or 0} ok, "
            f"{overview.failed_count or 0} failed, "
            f"{overview.error_count or 0} error, {overview.pending_count or 0} pending"
        )


if __name__ == "__main__":
    main()
