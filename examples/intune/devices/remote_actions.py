"""
Remote actions on a managed device: sync, reboot, lock, shut down, retire, wipe.

These are the day-to-day "do something to that device" commands. They are
**fire-and-forget**: Graph accepts the command (``204 No Content``) and the
device applies it the next time it checks in, so there is no result to poll.

Because ``retire`` and ``wipe`` are irreversible, the script is a **dry run by
default** — it prints what it would do. Add ``--apply`` to actually send the
command, and ``--yes`` for the destructive actions:

    python remote_actions.py --device-name LAPTOP --action sync            # plan only
    python remote_actions.py --device-name LAPTOP --action sync --apply
    python remote_actions.py --device-name LAPTOP --action wipe --apply --yes

Requires delegated permission
``DeviceManagementManagedDevices.PrivilegedOperations.All``.

https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-syncdevice
https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-retire
https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-wipe
"""

from __future__ import annotations

import argparse
import sys

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username

DESTRUCTIVE = ("retire", "wipe")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a remote action on a managed device")
    parser.add_argument("--device-name", default="", help="Substring to match a device name")
    parser.add_argument(
        "--action",
        choices=["sync", "reboot", "lock", "shutdown", "retire", "wipe"],
        default="sync",
        help="Remote action to run (default: sync)",
    )
    parser.add_argument("--apply", action="store_true", help="Actually send the command (default: dry run)")
    parser.add_argument("--yes", action="store_true", help="Confirm a destructive retire/wipe")
    args = parser.parse_args()

    if args.action in DESTRUCTIVE and args.apply and not args.yes:
        sys.exit(f"'{args.action}' is destructive — re-run with --apply --yes to confirm.")

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
    print(f"Device: {device.device_name}  (compliance: {device.compliance_state or 'unknown'})")
    print(f"Action: {args.action}")

    if not args.apply:
        print("\n[dry run] nothing was sent — add --apply to execute.")
        return

    actions = {
        "sync": device.sync_device,
        "reboot": device.reboot_now,
        "lock": device.remote_lock,
        "shutdown": device.shut_down,
        "retire": device.retire,
        "wipe": device.wipe,
    }
    try:
        actions[args.action]().execute_query()
        print(f"\nSent '{args.action}'. The device applies it on its next check-in.")
    except ClientRequestException as exc:
        print(f"\n[skipped] {exc.code}: {exc.message}")
        print("Remote actions need DeviceManagementManagedDevices.PrivilegedOperations.All.")


if __name__ == "__main__":
    main()
