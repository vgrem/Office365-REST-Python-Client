"""
Managed-device inventory: filter and summarise the devices Intune manages.

This is the most common starting point — "what devices do we have, and how
healthy are they?". Everything is filtered server-side with ``$filter`` where
possible (``complianceState``, ``operatingSystem``, ``managedDeviceOwnerType``)
and paged with ``get_all()`` so it works on tenants with thousands of devices.

Examples
--------
    python inventory.py                              # every device
    python inventory.py --compliance noncompliant    # only non-compliant
    python inventory.py --os Windows --ownership company
    python inventory.py --stale-days 30 --csv devices.csv

Requires delegated permission ``DeviceManagementManagedDevices.ReadWrite.All``
(read is enough).

https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-list
"""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from enum import Enum

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def label(value) -> str:
    """Render an enum member, a raw value or ``None`` as a short readable label."""
    if value is None:
        return "unknown"
    return value.name if isinstance(value, Enum) else str(value)


def as_utc(value: datetime | None) -> datetime | None:
    """Treat a naive Graph timestamp as UTC so comparisons are timezone-safe."""
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def build_filter(args: argparse.Namespace) -> str:
    clauses = []
    if args.compliance:
        clauses.append(f"complianceState eq '{args.compliance}'")
    if args.os:
        clauses.append(f"operatingSystem eq '{args.os}'")
    if args.ownership:
        clauses.append(f"managedDeviceOwnerType eq '{args.ownership}'")
    return " and ".join(clauses)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory and filter managed devices")
    parser.add_argument("--compliance", help="compliant | noncompliant | conflict | error | unknown")
    parser.add_argument("--os", help="Operating system, e.g. Windows, iOS, Android, macOS")
    parser.add_argument("--ownership", help="company | personal | unknown")
    parser.add_argument("--stale-days", type=int, help="Only devices that have not synced in N days")
    parser.add_argument("--csv", help="Also write the result to this CSV path (default: the temp directory)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    query = client.device_management.managed_devices
    filter_text = build_filter(args)
    if filter_text:
        query = query.filter(filter_text)

    try:
        devices = list(query.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementManagedDevices.Read.All and re-run.")
        return

    if args.stale_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.stale_days)
        devices = [d for d in devices if (as_utc(d.last_sync_date_time) or cutoff) < cutoff]

    if not devices:
        print("No managed devices matched.")
        return

    print(f"{len(devices)} device(s)  {filter_text or ''}".rstrip())
    for device in devices:
        print(
            f"  {device.device_name or '(unnamed)':30s}  {label(device.compliance_state):12s}"
            f"  {(device.operating_system or '?'):8s} {device.os_version or '':10s}"
            f"  [{label(device.managed_device_owner_type)}]"
            f"  last sync: {device.last_sync_date_time or 'never'}"
        )

    print("\nBy compliance:")
    for state, count in sorted(Counter(label(d.compliance_state) for d in devices).items()):
        print(f"  {state:14s} {count}")

    if args.csv:
        target = args.csv if os.path.isabs(args.csv) else os.path.join(tempfile.gettempdir(), args.csv)
        with open(target, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                ["deviceName", "complianceState", "operatingSystem", "osVersion", "serialNumber", "lastSync"]
            )
            for device in devices:
                writer.writerow(
                    [
                        device.device_name,
                        label(device.compliance_state),
                        device.operating_system,
                        device.os_version,
                        device.serial_number,
                        device.last_sync_date_time,
                    ]
                )
        print(f"\nWrote {target}")


if __name__ == "__main__":
    main()
