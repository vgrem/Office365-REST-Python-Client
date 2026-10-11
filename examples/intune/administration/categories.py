"""
Administration helpers: device categories, notification templates and terms.

Three small admin datasets that support the rest of Intune:

* **device categories** let admins group devices by purpose (e.g. "Kiosk"),
  usually chosen by the user during enrollment;
* **notification message templates** are the branded emails Intune sends
  (non-compliance, enrollment);
* **terms and conditions** are the agreements users must accept before they get
  access to corporate resources.

    python categories.py              # device categories
    python categories.py --templates  # + notification templates
    python categories.py --terms      # + terms and conditions

Requires delegated permission ``DeviceManagementServiceConfig.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-devices-devicecategory-list
https://learn.microsoft.com/en-us/graph/api/intune-notification-notificationmessagetemplate-list
https://learn.microsoft.com/en-us/graph/api/intune-companyterms-termsandconditions-list
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="List Intune administration datasets")
    parser.add_argument("--templates", action="store_true", help="Also list notification message templates")
    parser.add_argument("--terms", action="store_true", help="Also list terms and conditions")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    dm = client.device_management

    try:
        categories = list(dm.device_categories.get_all().execute_query())
        print(f"Device categories ({len(categories)}):")
        for category in categories:
            print(f"  {category.display_name or '(unnamed)':30s} {category.description or ''}".rstrip())
    except ClientRequestException as exc:
        print(f"[skipped] categories: {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementServiceConfig.Read.All and re-run.")

    if args.templates:
        try:
            templates = list(dm.notification_message_templates.get_all().execute_query())
            print(f"\nNotification templates ({len(templates)}):")
            for template in templates:
                print(
                    f"  {template.display_name or '(unnamed)':30s} locale: {template.default_locale or '?'}"
                    f"  modified: {template.last_modified_date_time or '?'}"
                )
        except ClientRequestException as exc:
            print(f"\n[skipped] notification templates: {exc.code}")

    if args.terms:
        try:
            terms = list(dm.terms_and_conditions.get_all().execute_query())
            print(f"\nTerms and conditions ({len(terms)}):")
            for item in terms:
                print(f"  {item.display_name or '(unnamed)':30s} v{item.version or '?'}  title: {item.title or '?'}")
            for item in terms:
                statuses = item.acceptance_statuses.get().execute_query()
                print(f"    '{item.display_name}': {len(statuses)} acceptance record(s)")
        except ClientRequestException as exc:
            print(f"\n[skipped] terms and conditions: {exc.code}")


if __name__ == "__main__":
    main()
