"""
The Intune lifecycle in one run — a read-only end-to-end walkthrough.

Intune is easiest to understand as a pipeline. Each stage below maps to the
folder that covers it, and each line is a live call against your tenant. Stages
your account cannot read are reported and skipped, so the script always exits 0.

    Enrol        enrollment/   configurations, Autopilot identities
    Register     devices/      managed devices appear, hardware, categories
    Configure    policies/     compliance policies and configuration profiles
    Protect      apps/         app catalogue, MAM policies, VPP tokens
    Manage       devices/      primary user, remote actions
    Govern       reports/      activity, enrollment failures, export jobs
    Audit        audit/        who changed what

    python lifecycle.py

Requires delegated permission ``DeviceManagementManagedDevices.ReadWrite.All``
plus whichever stage-specific permissions you have granted.

https://learn.microsoft.com/en-us/mem/intune/fundamentals/what-is-intune
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def stage(title: str) -> None:
    print(f"\n=== {title} ===")


def count(collection) -> int | None:
    """Return the item count for a collection, or ``None`` when access is denied."""
    try:
        return len(list(collection.get_all().execute_query()))
    except ClientRequestException as exc:
        print(f"  [skipped] {exc.code}: {exc.message}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk the Intune lifecycle against your tenant")
    parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    dm = client.device_management

    stage("1. Enrol — how devices are allowed in")
    if (enrollment := count(dm.device_enrollment_configurations)) is not None:
        print(f"  Enrollment configurations: {enrollment}")
    count(dm.windows_autopilot_device_identities)

    stage("2. Register — devices Intune now manages")
    if (devices := count(dm.managed_devices)) is not None:
        print(f"  Managed devices: {devices}")
    if (categories := count(dm.device_categories)) is not None:
        print(f"  Device categories: {categories}")

    stage("3. Configure — the rules pushed to those devices")
    if (policies := count(dm.device_compliance_policies)) is not None:
        print(f"  Compliance policies: {policies}")
    if (profiles := count(dm.device_configurations)) is not None:
        print(f"  Configuration profiles: {profiles}")

    stage("4. Protect — apps and their data-loss rules")
    if (apps := count(client.device_app_management.mobile_apps)) is not None:
        print(f"  Mobile apps: {apps}")
    if (mam := count(client.device_app_management.managed_app_policies)) is not None:
        print(f"  App protection policies: {mam}")
    if (vpp := count(client.device_app_management.vpp_tokens)) is not None:
        print(f"  VPP tokens: {vpp}")

    stage("5. Manage — acting on a single device")
    if devices:
        print(f"  {devices} device(s) available for sync / reboot / lock / retire / wipe.")
        print("  See devices/remote_actions.py (dry-run) and devices/primary_user.py.")
    else:
        print("  No managed devices to act on; see devices/remote_actions.py (dry-run).")

    stage("6. Govern — reports derived from the above")
    if (detected := count(dm.detected_apps)) is not None:
        print(f"  Detected apps: {detected}")
    try:
        overview = dm.managed_device_overview.get().execute_query()
        print(f"  Enrolled devices: {overview.enrolled_device_count or 0}")
    except ClientRequestException as exc:
        print(f"  [skipped] overview: {exc.code}")

    stage("7. Audit — who changed what")
    count(dm.audit_events)

    print("\nDone. Open a folder above to see the stage in detail.")


if __name__ == "__main__":
    main()
