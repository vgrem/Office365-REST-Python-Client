"""
Records management — create a retention label.

A retention label describes *when* a retention period starts, *how long* it
lasts, and *what happens* at the end (keep as record, then delete or start a
disposition review). Labels are defined once in the tenant and then applied to
content by users or by auto-apply policies.

    python create_label.py
    python create_label.py --name "Retain 7 Years" --days 2555

Requires delegated permission ``RecordsManagement.ReadWrite.All`` **and** the
Compliance Administrator (or Global Administrator) role.

https://learn.microsoft.com/en-us/graph/api/security-post-retentionlabels
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.security.labels.retention.actionafterretentionperiod import ActionAfterRetentionPeriod
from office365.security.labels.retention.behaviorduringretentionperiod import BehaviorDuringRetentionPeriod
from office365.security.labels.retention.defaultrecordbehavior import DefaultRecordBehavior
from office365.security.labels.retention.duration_in_days import RetentionDurationInDays
from office365.security.labels.retention.trigger import RetentionTrigger
from tests.settings import admin_username, client_id, tenant

_SCOPE = "RecordsManagement.ReadWrite.All"


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Compliance Administrator", "Global Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a retention label")
    parser.add_argument("--name", default="Retain 1 Year — Delete", help="Label display name")
    parser.add_argument("--days", type=int, default=365, help="Retention duration in days")
    args = parser.parse_args()

    client = _client()
    label = client.security.labels.retention_labels.add(
        args.name,
        RetentionTrigger.dateLabeled,
        RetentionDurationInDays(args.days),
        BehaviorDuringRetentionPeriod.retainAsRecord,
        DefaultRecordBehavior.startLocked,
        ActionAfterRetentionPeriod.delete,
    ).execute_query()

    duration = label.retention_duration
    print(f"Label created: {label.display_name}")
    print(f"  Trigger:          {label.retention_trigger}")
    print(f"  Duration:         {getattr(duration, 'days', duration)} day(s)")
    print(f"  End action:       {label.action_after_retention_period}")
    print(f"  Default behavior: {label.default_record_behavior}")
    print(f"  In use:           {label.is_in_use}")


if __name__ == "__main__":
    main()
