"""
App inventory: the applications Intune knows about, and their categories.

``mobile_apps`` is the catalogue of apps Intune can deploy — store apps, managed
store apps, Win32/LOB apps, web links. ``mobile_app_categories`` is the
admin-defined taxonomy used to organise them. Both are read-only here.

    python inventory.py              # list apps and categories
    python inventory.py --details    # + per-app categories and assignments

Requires delegated permission ``DeviceManagementApps.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-apps-mobileapp-list
https://learn.microsoft.com/en-us/graph/api/intune-apps-mobileappcategory-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory Intune mobile apps")
    parser.add_argument("--details", action="store_true", help="Show each app's categories and assignments")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    apps = client.device_app_management.mobile_apps

    try:
        items = list(apps.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementApps.Read.All and re-run.")
        return

    print(f"Mobile apps ({len(items)}):")
    for app in items:
        print(f"  {app.display_name or '(unnamed)':45s} {app.publisher or '':25s}  state: {app.publishing_state or '?'}")
        if not args.details:
            continue
        categories = app.categories.get().execute_query()
        assignments = app.assignments.get().execute_query()
        names = ", ".join(category.display_name or "?" for category in categories)
        print(f"      categories:  {names or '(none)'}")
        print(f"      assignments: {len(assignments)}")

    try:
        categories = list(client.device_app_management.mobile_app_categories.get_all().execute_query())
        print(f"\nCategories ({len(categories)}):")
        for category in categories:
            print(f"  {category.display_name or '(unnamed)'}")
    except ClientRequestException as exc:
        print(f"\n[skipped] categories: {exc.code}")


if __name__ == "__main__":
    main()
