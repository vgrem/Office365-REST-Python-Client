"""
Compliance: tenant-wide counts plus the per-policy state of a single device.

Two complementary views:

* the **summary** singletons give the whole-tenant picture
  (compliant / non-compliant / in-grace-period / error counts), and
* the **per-device** collections show which compliance and configuration
  policies a device is failing, which is what you need when a user opens a
  ticket.

    python compliance.py                       # tenant summary + every device
    python compliance.py --device-name LAPTOP   # which policies one device fails

Requires delegated permission ``DeviceManagementConfiguration.Read.All`` and
``DeviceManagementManagedDevices.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-list
https://learn.microsoft.com/en-us/graph/api/intune-onboarding-devicecompliancestatesummary-get
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def print_summary(client: GraphClient) -> None:
    """Print the tenant-wide compliance and configuration state summaries."""
    summary = client.device_management.device_compliance_policy_device_state_summary.get().execute_query()
    print("Compliance policy summary (tenant):")
    for name in (
        "compliant_device_count",
        "non_compliant_device_count",
        "in_grace_period_count",
        "error_device_count",
        "conflict_device_count",
        "unknown_device_count",
    ):
        print(f"  {name:28s} {getattr(summary, name) or 0}")

    configuration = client.device_management.device_configuration_device_state_summaries.get().execute_query()
    print("\nConfiguration profile summary (tenant):")
    for name in ("compliant_device_count", "non_compliant_device_count", "error_device_count", "conflict_device_count"):
        print(f"  {name:28s} {getattr(configuration, name) or 0}")


def print_device_states(device) -> None:
    """Print the per-policy states (compliance and configuration) for one device."""
    print(f"\n{device.device_name or '(unnamed)'}  [{device.compliance_state or 'unknown'}]")

    policies = device.device_compliance_policy_states.get().execute_query()
    print(f"  Compliance policies ({len(policies)}):")
    for state in policies:
        print(f"    {state.display_name or '(unnamed)':40s} {state.state or '?'}")

    profiles = device.device_configuration_states.get().execute_query()
    print(f"  Configuration profiles ({len(profiles)}):")
    for state in profiles:
        print(f"    {state.display_name or '(unnamed)':40s} {state.state or '?'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Show Intune compliance state")
    parser.add_argument("--device-name", help="Substring to match a device name (per-device detail)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    try:
        print_summary(client)
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementConfiguration.Read.All and re-run.")
        return

    query = client.device_management.managed_devices
    if args.device_name:
        name = args.device_name.replace("'", "''")
        query = query.filter(f"contains(deviceName, '{name}')")
    devices = list(query.get_all().execute_query())
    if not devices:
        print("\nNo managed devices matched.")
        return
    for device in devices:
        print_device_states(device)


if __name__ == "__main__":
    main()
