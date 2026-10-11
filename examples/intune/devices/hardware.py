"""
Device hardware and OS detail — the fields behind a refresh or support ticket.

Where the inventory gives you one line per device, this dumps the hardware
attributes admins actually quote: manufacturer, model, serial/IMEI, memory,
storage and enrollment date. Pass ``--device-name`` to zoom into one device.

    python hardware.py                       # hardware for every device
    python hardware.py --device-name LAPTOP   # a single device (substring match)

Requires delegated permission ``DeviceManagementManagedDevices.ReadWrite.All``
(read is enough).

https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def gib(value: int | None) -> str:
    """Format a byte count as gibibytes."""
    return f"{value / (1024**3):.1f} GiB" if value else "?"


def print_device(device) -> None:
    print(f"{device.device_name or '(unnamed)':30s}  [{device.compliance_state or 'unknown'}]")
    print(f"    OS:        {(device.operating_system or '?')} {device.os_version or ''}".rstrip())
    print(f"    Hardware:  {(device.manufacturer or '?')} {device.model or ''}".rstrip())
    print(f"    Serial:    {device.serial_number or '?'}  IMEI: {device.imei or '?'}")
    print(f"    Memory:    {gib(device.physical_memory_in_bytes)}")
    print(f"    Storage:   {gib(device.total_storage_space_in_bytes)} (free {gib(device.free_storage_space_in_bytes)})")
    print(f"    Enrolled:  {device.enrolled_date_time or '?'}  Last sync: {device.last_sync_date_time or '?'}")
    print(f"    Managed:   agent={device.management_agent or '?'}  state={device.management_state or '?'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Show hardware detail for managed devices")
    parser.add_argument("--device-name", help="Substring to match a device name")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        if args.device_name:
            name = args.device_name.replace("'", "''")
            devices = list(
                client.device_management.managed_devices.filter(f"contains(deviceName, '{name}')").get().execute_query()
            )
        else:
            devices = list(client.device_management.managed_devices.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementManagedDevices.Read.All and re-run.")
        return

    if not devices:
        print("No managed devices matched.")
        return

    print(f"Hardware detail for {len(devices)} device(s)\n")
    for device in devices:
        print_device(device)
        print()


if __name__ == "__main__":
    main()
