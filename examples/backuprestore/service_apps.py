"""
List the third-party backup applications registered with the tenant.

A "service app" is a multi-tenant application that provides the Backup Storage
service itself. Registering and (de)activating it is how Microsoft 365 Backup is
onboarded; ``activate`` takes the date-time from which the app is effective.
Both write actions are no-ops unless ``--apply`` is given.

Requires delegated or application permission
``BackupRestore-Control.ReadWrite.All``. On an unlicensed tenant the call is
denied and a short license hint is printed.

https://learn.microsoft.com/en-us/graph/api/backuprestoreroot-list-serviceapps
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _run(client: GraphClient, args: argparse.Namespace) -> None:
    apps = client.solutions.backup_restore.service_apps.get().execute_query()
    print(f"Registered backup service apps ({len(apps)}):")
    for app in apps:
        print(f"  {app.id}  status={app.status}  application={app.application}")
        print(f"      effective={app.effective_date_time}  registered={app.registration_date_time}")

    if args.activate:
        app = client.solutions.backup_restore.service_apps[args.activate]
        if args.apply:
            app.activate(args.effective_date_time).execute_query()
            print(f"\nActivated service app {args.activate} effective {args.effective_date_time}.")
        else:
            print(f"\nDry run. Would POST activate for service app {args.activate}.")
    elif args.deactivate:
        app = client.solutions.backup_restore.service_apps[args.deactivate]
        if args.apply:
            app.deactivate().execute_query()
            print(f"\nDeactivated service app {args.deactivate}.")
        else:
            print(f"\nDry run. Would POST deactivate for service app {args.deactivate}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="List (and activate) Backup Storage service apps")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--activate", metavar="SERVICE_APP_ID", help="Activate this service app")
    group.add_argument("--deactivate", metavar="SERVICE_APP_ID", help="Deactivate this service app")
    parser.add_argument(
        "--effective-date-time",
        type=datetime.fromisoformat,
        default=datetime.now(timezone.utc),
        help="Effective date-time for --activate (ISO 8601; default: now)",
    )
    parser.add_argument("--apply", action="store_true", help="Actually perform the action")
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
