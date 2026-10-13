"""
Search the restore points that a restore can be started from.

There is no plain "list restore points" API: the tenant's ``restorePoints``
collection exposes a ``search`` action that is scoped by protection unit, by
time window and by tag, and can prefer the latest or the oldest matching point.

Requires delegated or application permission ``BackupRestore-Control.Read.All``.
On an unlicensed tenant the call is denied and a short license hint is printed.

https://learn.microsoft.com/en-us/graph/api/restorepoint-search
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.backuprestore.restorepoints.preference import RestorePointPreference
from office365.backuprestore.restorepoints.tags import RestorePointTags
from office365.backuprestore.time_period import TimePeriod
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _run(client: GraphClient, args: argparse.Namespace) -> None:
    period = TimePeriod()
    period.endDateTime = datetime.now(timezone.utc)
    period.startDateTime = period.endDateTime - timedelta(days=args.days)

    result = client.solutions.backup_restore.restore_points.search(
        protection_time_period=period,
        restore_point_preference=RestorePointPreference.latest,
        tags=RestorePointTags.none,
    ).execute_query()

    response = result.value
    print(f"Search id: {response.searchResponseId}")
    print(f"Protection units without a match: {list(response.noResultProtectionUnitIds)}")
    print(f"Matches ({len(response.searchResults)}):")
    for match in response.searchResults:
        point = match.restorePoint
        if point is None:
            continue
        print(f"  {point.id}  protected={point.protection_date_time}  expires={point.expiration_date_time}")
        print(f"      tags: {point.tags}  artifacts: {match.artifactHitCount}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Backup Storage restore points")
    parser.add_argument("--days", type=int, default=30, help="Look back this many days (default: 30)")
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
