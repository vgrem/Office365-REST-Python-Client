"""
Enable the Microsoft 365 Backup Storage service for the tenant.

The ``enable`` API must be called by a **multi-tenant** app registered in
*another* tenant that holds the Backup Storage permission — pass that tenant's
id as ``--app-owner-tenant-id``. The call is a no-op unless ``--apply`` is
given, so the script is safe to run for inspection.

Requires delegated or application permission
``BackupRestore-Control.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/backuprestoreroot-enable
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="Enable Microsoft 365 Backup Storage")
    parser.add_argument("--app-owner-tenant-id", required=True, help="Tenant id of the multi-tenant app owner")
    parser.add_argument("--apply", action="store_true", help="Actually submit the enable request")
    args = parser.parse_args()

    if not args.apply:
        print("Dry run. Would call POST /solutions/backupRestore/enable with:")
        print(f"  appOwnerTenantId = {args.app_owner_tenant_id}")
        print("Re-run with --apply to submit the request.")
        return

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    try:
        result = client.solutions.backup_restore.enable(args.app_owner_tenant_id).execute_query()
    except ClientRequestException as err:
        print("Unable to enable Microsoft 365 Backup Storage.")
        print("The enabling app must be multi-tenant, registered in another tenant,")
        print("and hold BackupRestore-Control.ReadWrite.All. See README.md.")
        print(f"\nServer response: {err}")
        return

    print("Backup Storage enable request submitted:")
    print(f"  Status:   {result.value.status}")
    print(f"  Consumer: {result.value.backupServiceConsumer}")


if __name__ == "__main__":
    main()
