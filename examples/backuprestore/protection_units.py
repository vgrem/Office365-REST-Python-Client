"""
List the protection units of every Backup Storage workload.

A protection unit is a protected mailbox, OneDrive or SharePoint site. The
script also shows (and, with ``--apply``, performs) the asynchronous
``offboard`` / ``cancelOffboard`` actions that remove a unit from its policy.

Requires delegated or application permission
``BackupRestore-Control.Read.All`` (``ReadWrite.All`` for offboarding). On an
unlicensed tenant the call is denied and a short license hint is printed.

https://learn.microsoft.com/en-us/graph/api/backuprestoreroot-list-driveprotectionunits
"""

from __future__ import annotations

import argparse
from datetime import datetime
from typing import Sequence

from office365.backuprestore.protection_unit_base import ProtectionUnitBase
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _print_units(label: str, units: Sequence[ProtectionUnitBase]) -> None:
    print(f"{label} ({len(units)}):")
    for unit in units:
        print(f"  {unit.id}  status={unit.status}  policy={unit.policy_id}")
        if unit.offboard_requested_date_time != datetime.min:
            print(f"      offboard requested: {unit.offboard_requested_date_time}")


def _run(client: GraphClient, args: argparse.Namespace) -> None:
    backup = client.solutions.backup_restore
    _print_units("Drive protection units", list(backup.drive_protection_units.get().execute_query()))
    _print_units("Mailbox protection units", list(backup.mailbox_protection_units.get().execute_query()))
    _print_units("Site protection units", list(backup.site_protection_units.get().execute_query()))

    if args.offboard:
        unit = backup.drive_protection_units[args.offboard]
        if args.apply:
            unit.offboard().execute_query()
            print(f"\nRequested offboard of drive protection unit {args.offboard}.")
        else:
            print(f"\nDry run. Would POST offboard for drive protection unit {args.offboard}.")
    elif args.cancel_offboard:
        unit = backup.drive_protection_units[args.cancel_offboard]
        if args.apply:
            unit.cancel_offboard().execute_query()
            print(f"\nCancelled offboard of drive protection unit {args.cancel_offboard}.")
        else:
            print(f"\nDry run. Would POST cancelOffboard for drive protection unit {args.cancel_offboard}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="List Backup Storage protection units")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--offboard", metavar="DRIVE_UNIT_ID", help="Offboard the given drive protection unit")
    group.add_argument("--cancel-offboard", metavar="DRIVE_UNIT_ID", help="Cancel a pending offboard request")
    parser.add_argument("--apply", action="store_true", help="Actually perform the offboard action")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    try:
        _run(client, args)
    except ClientRequestException as err:
        print("Microsoft 365 Backup Storage is not available on this tenant.")
        print("It is a paid add-on and must be enabled; see README.md -> 'Licensing'.")
        print(f"\nServer response: {err}")


if __name__ == "__main__":
    main()
