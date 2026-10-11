"""
Protection overview: the third-party services and conditional access Intune talks to.

Intune does not protect devices alone. It integrates with:

* **compliance partners** (e.g. an MDM/EMM coexistence service),
* **device-management partners** (co-management with Configuration Manager),
* **Exchange connectors** (Exchange ActiveSync device access),
* **mobile threat defence** (MTD) connectors, and
* **on-premises conditional access** (hybrid Exchange/Azure AD).

This script walks all of them and flags connectors whose heartbeat is stale,
which is the usual reason compliance signals stop flowing.

    python overview.py

Requires delegated permission ``DeviceManagementServiceConfig.Read.All`` and
``DeviceManagementConfiguration.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-onboarding-devicemanagementpartner-list
https://learn.microsoft.com/en-us/graph/api/intune-onboarding-onpremisesconditionalaccesssettings-get
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def as_utc(value: datetime | None) -> datetime | None:
    """Treat a naive Graph timestamp as UTC so comparisons are timezone-safe."""
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def age(value: datetime | None) -> str:
    moment = as_utc(value)
    if moment is None:
        return "never"
    return "stale" if moment < datetime.now(timezone.utc) - timedelta(days=1) else "fresh"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarise Intune protection integrations")
    parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    dm = client.device_management

    try:
        conditional = dm.conditional_access_settings.get().execute_query()
        print(
            f"On-premises conditional access: {'enabled' if conditional.enabled else 'disabled'}"
            f"  ({len(conditional.included_groups)} group(s) included)"
        )
    except ClientRequestException as exc:
        print(f"[skipped] conditional access: {exc.code}")

    try:
        partners = list(dm.device_management_partners.get_all().execute_query())
        print(f"\nDevice-management partners ({len(partners)}):")
        for partner in partners:
            print(
                f"  {partner.display_name or '(unnamed)':30s} {partner.partner_state or '?'}"
                f"  heartbeat: {partner.last_heartbeat_date_time or 'never'} [{age(partner.last_heartbeat_date_time)}]"
            )
    except ClientRequestException as exc:
        print(f"\n[skipped] device-management partners: {exc.code}")

    try:
        compliance_partners = list(dm.compliance_management_partners.get_all().execute_query())
        print(f"\nCompliance partners ({len(compliance_partners)}):")
        for partner in compliance_partners:
            print(
                f"  {partner.display_name or '(unnamed)':30s} {partner.partner_state or '?'}"
                f"  heartbeat: {partner.last_heartbeat_date_time or 'never'} [{age(partner.last_heartbeat_date_time)}]"
            )
    except ClientRequestException as exc:
        print(f"\n[skipped] compliance partners: {exc.code}")

    try:
        connectors = list(dm.exchange_connectors.get_all().execute_query())
        print(f"\nExchange connectors ({len(connectors)}):")
        for connector in connectors:
            print(
                f"  {connector.exchange_alias or '(unnamed)':30s} {connector.status or '?'}"
                f"  last sync: {connector.last_sync_date_time or 'never'}"
            )
    except ClientRequestException as exc:
        print(f"\n[skipped] Exchange connectors: {exc.code}")

    try:
        mtd = list(dm.mobile_threat_defense_connectors.get_all().execute_query())
        print(f"\nMobile threat defence connectors ({len(mtd)}):")
        for connector in mtd:
            print(
                f"  android={connector.android_enabled} ios={connector.ios_enabled}"
                f"  heartbeat: {connector.last_heartbeat_date_time or 'never'}"
            )
    except ClientRequestException as exc:
        print(f"\n[skipped] threat defence connectors: {exc.code}")


if __name__ == "__main__":
    main()
