"""
Device configuration activity reports.

Graph exposes Intune's aggregate activity as report functions on
``client.reports``. Each returns a ``Report`` object whose ``content`` holds the
raw payload (the tenant above returns an empty body when there is no data, so
the script prints the size rather than assuming a value).

    python device_activity.py

Requires delegated permission ``DeviceManagementConfiguration.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-deviceconfig-reportroot-deviceconfigurationuseractivity
https://learn.microsoft.com/en-us/graph/api/intune-deviceconfig-reportroot-deviceconfigurationdeviceactivity
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def report_size(result) -> str:
    """Return a short description of a report result, tolerating an empty body."""
    try:
        report = result.value
    except AssertionError:
        return "no content"
    content = report.to_bytes() if hasattr(report, "to_bytes") else b""
    return f"{len(content)} byte(s)" if content else "empty"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Intune device activity reports")
    parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    reports = {
        "Device configuration user activity": client.reports.device_configuration_user_activity,
        "Device configuration device activity": client.reports.device_configuration_device_activity,
    }

    for title, factory in reports.items():
        try:
            result = factory().execute_query()
            print(f"{title}: {report_size(result)}")
        except ClientRequestException as exc:
            print(f"{title}: [skipped] {exc.code}: {exc.message}")
            print("  Grant admin consent for DeviceManagementConfiguration.Read.All and re-run.")


if __name__ == "__main__":
    main()
