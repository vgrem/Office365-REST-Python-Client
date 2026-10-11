"""
Compliance policies: what is enforced, and how many devices pass.

A compliance policy defines the conditions a device must meet (PIN, encryption,
OS version, jailbreak). This script lists every policy, its assignment count and
— with ``--details`` — the groups it targets and the device status rollup.

    python compliance_policies.py                # list policies
    python compliance_policies.py --details      # + assignments and statuses

Requires delegated permission ``DeviceManagementConfiguration.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-devices-devicecompliancepolicy-list
https://learn.microsoft.com/en-us/graph/api/intune-devices-devicecompliancepolicyassignment-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="List Intune compliance policies")
    parser.add_argument("--details", action="store_true", help="Also show assignments and device status")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        policies = list(client.device_management.device_compliance_policies.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementConfiguration.Read.All and re-run.")
        return

    print(f"Compliance policies ({len(policies)}):")
    if not policies:
        return

    for policy in policies:
        created = policy.created_date_time or "?"
        print(f"  {policy.display_name or '(unnamed)':45s} v{policy.version or '?'}  created: {created}")
        if not args.details:
            continue
        assignments = policy.assignments.get().execute_query()
        print(f"    Assigned to {len(assignments)} target(s)")
        overview = policy.device_status_overview.get().execute_query()
        print(
            f"    Devices: {overview.success_count or 0} ok, "
            f"{overview.failed_count or 0} failed, "
            f"{overview.error_count or 0} error, {overview.pending_count or 0} pending"
        )


if __name__ == "__main__":
    main()
