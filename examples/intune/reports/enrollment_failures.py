"""
Enrollment failure reports: why devices failed to enrol.

When enrollment goes wrong, these two reports explain it. Both return a
``Report`` whose ``content`` is the actual payload (often empty when there is
nothing to report), so the script prints its size and, when present, decodes it.

    python enrollment_failures.py
    python enrollment_failures.py --period D30

Requires delegated permission ``DeviceManagementManagedDevices.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddeviceenrollmentfailuredetails
https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddeviceenrollmenttopfailures
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def show(title: str, result) -> None:
    try:
        report = result.value
    except AssertionError:
        print(f"{title}: no content")
        return
    content = report.to_bytes() if hasattr(report, "to_bytes") else b""
    if not content:
        print(f"{title}: empty")
        return
    print(f"{title}: {len(content)} byte(s)")
    print(content.decode("utf-8", errors="replace")[:500])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Intune enrollment failure reports")
    parser.add_argument("--period", default=None, help="Top-failures period, e.g. D7, D30 (default: all time)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        show("Enrollment failure details", client.reports.managed_device_enrollment_failure_details().execute_query())
        show(
            "Top enrollment failures",
            client.reports.managed_device_enrollment_top_failures(args.period).execute_query(),
        )
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementManagedDevices.Read.All and re-run.")


if __name__ == "__main__":
    main()
