"""
Read the tenant's Backup Storage email-notification setting.

When enabled, the tenant receives email notifications about restore operations
and protection-policy updates. The setting is a singleton under
``backupRestore/emailNotificationsSetting``; the script can also flip
``isEnabled`` (a no-op unless ``--apply`` is given).

Requires delegated or application permission
``BackupRestore-Control.ReadWrite.All``. On an unlicensed tenant the call is
denied and a short license hint is printed.

https://learn.microsoft.com/en-us/graph/api/backuprestoreroot-get-emailnotificationssetting
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _run(client: GraphClient, args: argparse.Namespace) -> None:
    setting = client.solutions.backup_restore.email_notifications_setting.get().execute_query()

    print("Email notifications setting:")
    print(f"  enabled: {setting.is_enabled}")
    print(f"  events:  {setting.additional_events}")
    print(f"  role:    {setting.recipients.role}")
    print(f"  custom recipients ({len(setting.recipients.customRecipients)}):")
    for recipient in setting.recipients.customRecipients:
        print(f"    - {recipient.displayName or recipient.email}")

    enabled = args.enable or (False if args.disable else None)
    if enabled is None:
        return

    if not args.apply:
        print(f"\nDry run. Would set isEnabled={enabled}.")
        return

    setting.set_property("isEnabled", enabled)
    setting.update().execute_query()
    print(f"\nUpdated isEnabled to {enabled}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read/update Backup Storage email notifications")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enable", action="store_true", help="Enable email notifications")
    group.add_argument("--disable", action="store_true", help="Disable email notifications")
    parser.add_argument("--apply", action="store_true", help="Actually update the setting")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    try:
        _run(client, args)
    except ClientRequestException as err:
        print("Microsoft 365 Backup Storage is not available on this tenant.")
        print("It is a paid add-on and must be enabled; see README.md -> 'Licensing'.")
        print(f"\nServer response: {err}")


if __name__ == "__main__":
    main()
