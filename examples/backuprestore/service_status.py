"""
Check the Microsoft 365 Backup Storage service status.

Reads the tenant-wide ``serviceStatus`` object (status, consumer, grace period
and disable reason) from ``GET /solutions/backupRestore``.

Requires delegated or application permission ``BackupRestore-Control.Read.All``.
Microsoft 365 Backup Storage is a **paid add-on**: on an unlicensed tenant the
call is denied and this example prints a short explanation instead of a
traceback. See ``README.md`` for the licensing details.

https://learn.microsoft.com/en-us/graph/api/backuprestoreroot-list-servicestatus
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    backup = client.solutions.backup_restore
    try:
        backup.get().execute_query()
    except ClientRequestException as err:
        print("Microsoft 365 Backup Storage is not available on this tenant.")
        print("It is a paid add-on and must be enabled before this API can be used.")
        print("See README.md -> 'Licensing' for the full picture.")
        print(f"\nServer response: {err}")
        return

    status = backup.service_status
    print("Microsoft 365 Backup Storage service status:")
    print(f"  Status:            {status.status}")
    print(f"  Consumer:          {status.backupServiceConsumer}")
    print(f"  Disable reason:    {status.disableReason}")
    print(f"  Grace period till: {status.gracePeriodDateTime}")
    print(f"  Restore allowed:   {status.restoreAllowedTillDateTime}")


if __name__ == "__main__":
    main()
