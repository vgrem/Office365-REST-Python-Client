"""
Enrollment configurations: the rules that decide how devices can enrol.

Enrollment configurations (formerly "enrollment restrictions") control *who* can
enrol and *how many* devices they may have — platform allow/block lists,
per-user device limits, and priority order. This is the "registration" gate in
the Intune lifecycle.

    python configurations.py              # list configurations
    python configurations.py --details    # + assignment counts

Requires delegated permission ``DeviceManagementServiceConfig.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-onboarding-deviceenrollmentconfiguration-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="List Intune enrollment configurations")
    parser.add_argument("--details", action="store_true", help="Also show assignments")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        configurations = list(client.device_management.device_enrollment_configurations.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementServiceConfig.Read.All and re-run.")
        return

    print(f"Enrollment configurations ({len(configurations)}):")
    for configuration in configurations:
        print(
            f"  {configuration.display_name or '(unnamed)':40s} priority: {configuration.priority or '?'}"
            f"  v{configuration.version or '?'}"
        )
        if args.details:
            assignments = configuration.assignments.get().execute_query()
            print(f"      assigned to {len(assignments)} target(s)")


if __name__ == "__main__":
    main()
