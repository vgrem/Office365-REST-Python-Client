"""
Microsoft Intune quickstart: connect and take stock of a tenant.

Prints the managed-device count, a compliance breakdown and the enrollment
overview, so you can confirm your credentials and consent before exploring the
rest of this folder. It also lists the installed-app count when that permission
is available.

Intune is exposed through two Graph singletons: ``client.device_management``
(devices, policies, reports, audit) and ``client.device_app_management`` (apps,
app-protection policies, VPP tokens). A read-only account needs an Intune role
and one of the ``DeviceManagement*`` permissions described in the README.

Requires delegated permission ``DeviceManagementManagedDevices.ReadWrite.All``
(read is enough) and, optionally, ``DeviceManagementApps.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-list
https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddeviceoverview-get
"""

from __future__ import annotations

import argparse
from collections import Counter
from enum import Enum

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def label(value) -> str:
    """Render an enum member, a raw value or ``None`` as a short readable label."""
    if value is None:
        return "unknown"
    return value.name if isinstance(value, Enum) else str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Connect to Intune and summarise the tenant")
    parser.add_argument("--top", type=int, default=10, help="How many device names to print (default: 10)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    try:
        devices = list(client.device_management.managed_devices.get().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementManagedDevices.Read.All and re-run.")
        return

    print(f"Managed devices: {len(devices)}")
    breakdown = Counter(label(d.compliance_state) for d in devices)
    for state, count in sorted(breakdown.items()):
        print(f"  {state:14s} {count}")

    for device in devices[: args.top]:
        print(f"    {device.device_name or '(unnamed)':30s} last sync: {device.last_sync_date_time or 'never'}")

    try:
        overview = client.device_management.managed_device_overview.get().execute_query()
        print(
            f"\nEnrollment: {overview.enrolled_device_count or 0} enrolled "
            f"({overview.mdm_enrolled_count or 0} MDM, {overview.dual_enrolled_device_count or 0} dual)"
        )
    except ClientRequestException as exc:
        print(f"\n[skipped] enrollment overview: {exc.code}")

    try:
        apps = list(client.device_app_management.mobile_apps.get().execute_query())
        print(f"Mobile apps: {len(apps)}")
    except ClientRequestException as exc:
        print(f"[skipped] mobile apps: {exc.code} (needs DeviceManagementApps.Read.All)")


if __name__ == "__main__":
    main()
