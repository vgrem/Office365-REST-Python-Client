"""
Windows Autopilot: the hardware identities that can be provisioned to zero-touch.

Autopilot devices are registered by hardware hash *before* anyone turns them on.
The identity (serial, model, group tag) tells Autopilot which deployment profile
to apply, so the device self-provisions on first boot. ``imported`` identities
are hashes staged but not yet turned into Autopilot devices.

    python autopilot.py               # registered Autopilot devices
    python autopilot.py --imported    # + staged (imported) identities

Requires delegated permission ``DeviceManagementServiceConfig.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-enrollment-windowsautopilotdeviceidentity-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def dump(identities) -> None:
    for identity in identities:
        print(
            f"  {identity.serial_number or '(no serial)':20s} "
            f"{(identity.manufacturer or '?')} {(identity.model or ''):20s} "
            f"tag: {identity.group_tag or '-':12s} state: {identity.enrollment_state or '?'}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="List Windows Autopilot device identities")
    parser.add_argument("--imported", action="store_true", help="Also list staged (imported) identities")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    try:
        identities = list(client.device_management.windows_autopilot_device_identities.get_all().execute_query())
        print(f"Autopilot devices ({len(identities)}):")
        dump(identities)
    except ClientRequestException as exc:
        print(f"[skipped] Autopilot devices: {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementServiceConfig.Read.All and re-run.")
        return

    if args.imported:
        try:
            imported = list(
                client.device_management.imported_windows_autopilot_device_identities.get_all().execute_query()
            )
            print(f"\nStaged identities ({len(imported)}):")
            dump(imported)
        except ClientRequestException as exc:
            print(f"\n[skipped] staged identities: {exc.code}")


if __name__ == "__main__":
    main()
