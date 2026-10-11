"""
Primary user and device ownership — who carries the device, and whose data it is.

A managed device has a *primary user* (the person enrolled or assigned it) and an
*ownership* type (``company`` or ``personal``). Both matter for compliance
attribution and for conditional-access decisions. This script reads them, and can
assign/remove the primary user or flip ownership.

    python primary_user.py --device-name LAPTOP                # show (default)
    python primary_user.py --device-name LAPTOP --action assign --user-id <guid>
    python primary_user.py --device-name LAPTOP --action remove --user-id <guid>
    python primary_user.py --device-name LAPTOP --action set-ownership --ownership personal

Writes need ``DeviceManagementManagedDevices.PrivilegedOperations.All``; the
script reports the missing scope instead of failing.

Requires delegated permission ``DeviceManagementManagedDevices.ReadWrite.All``
and, for changes, ``DeviceManagementManagedDevices.PrivilegedOperations.All``.

https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-users
https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-update
"""

from __future__ import annotations

import argparse
import sys

from office365.graph_client import GraphClient
from office365.intune.devices.management.managed.ownertype import ManagedDeviceOwnerType
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def show(device) -> None:
    print(f"  Primary user: {(device.user_display_name or '?')} ({device.user_principal_name or '?'})")
    print(f"  Email:        {device.email_address or '?'}")
    print(f"  Ownership:    {device.managed_device_owner_type or '?'}")
    print(f"  User id:      {device.user_id or '?'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read or change a device's primary user and ownership")
    parser.add_argument("--device-name", default="", help="Substring to match a device name")
    parser.add_argument("--user-id", help="Directory object id of the user (assign/remove)")
    parser.add_argument("--ownership", choices=["company", "personal"], help="Target ownership (set-ownership)")
    parser.add_argument(
        "--action",
        choices=["show", "assign", "remove", "set-ownership"],
        default="show",
        help="What to do (default: show)",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    name = args.device_name.replace("'", "''")
    query = client.device_management.managed_devices
    if name:
        query = query.filter(f"contains(deviceName, '{name}')")

    try:
        devices = list(query.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementManagedDevices.Read.All and re-run.")
        return

    if not devices:
        print("No managed devices matched.")
        return

    device = devices[0]
    print(f"Device: {device.device_name}  (compliance: {device.compliance_state or 'unknown'})\n")

    if args.action == "show":
        show(device)
        return

    if args.action in ("assign", "remove") and not args.user_id:
        sys.exit("--user-id is required for assign/remove")
    if args.action == "set-ownership" and not args.ownership:
        sys.exit("--ownership is required for set-ownership")

    try:
        if args.action == "assign":
            device.set_primary_user(args.user_id).execute_query()
            print(f"  Assigned primary user {args.user_id}")
        elif args.action == "remove":
            device.remove_primary_user(args.user_id).execute_query()
            print(f"  Removed user {args.user_id}")
        else:
            device.set_property("managedDeviceOwnerType", ManagedDeviceOwnerType[args.ownership], True)
            device.update().execute_query()
            print(f"  Ownership set to '{args.ownership}'")
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Privileged changes need DeviceManagementManagedDevices.PrivilegedOperations.All.")


if __name__ == "__main__":
    main()
