"""
Records management — apply a retention label to aging, unlabeled files.

Walks every site's default document library and finds files that are old (older
than ``--days``) but still carry no retention label. That is the typical
"legacy content has no retention" gap. The script prints what it would do and
only applies labels when you pass ``--apply``.

    python auto_apply.py                 # dry run
    python auto_apply.py --apply         # actually label the files
    python auto_apply.py --label "Retain 7 Years" --days 2555 --limit 50

Requires delegated permission ``RecordsManagement.ReadWrite.All`` and
``Sites.ReadWrite.All``, plus the Compliance Administrator (or Global
Administrator) role.

https://learn.microsoft.com/en-us/graph/api/driveitem-update
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.security.labels.retention.actionafterretentionperiod import ActionAfterRetentionPeriod
from office365.security.labels.retention.behaviorduringretentionperiod import BehaviorDuringRetentionPeriod
from office365.security.labels.retention.defaultrecordbehavior import DefaultRecordBehavior
from office365.security.labels.retention.duration_in_days import RetentionDurationInDays
from office365.security.labels.retention.trigger import RetentionTrigger
from tests.settings import admin_username, client_id, tenant

_SKIP_LIBRARIES = ("Preservation Hold", "Wiki Data", "App Catalog", "Form Templates")


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Compliance Administrator", "Global Administrator")
    )


def _find_label(client: GraphClient, name: str):
    labels = client.security.labels.retention_labels.get().execute_query()
    return next((label for label in labels if label.display_name == name), None)


def _ensure_label(client: GraphClient, name: str, days: int):
    label = _find_label(client, name)
    if label is None:
        label = client.security.labels.retention_labels.add(
            name,
            RetentionTrigger.dateLabeled,
            RetentionDurationInDays(days),
            BehaviorDuringRetentionPeriod.retainAsRecord,
            DefaultRecordBehavior.startLocked,
            ActionAfterRetentionPeriod.delete,
        ).execute_query()
        print(f"Created label: {label.display_name}")
    return label


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a retention label to aging, unlabeled files")
    parser.add_argument("--label", default="Auto-Retain-365D", help="Retention label display name")
    parser.add_argument("--days", type=int, default=365, help="File age threshold in days")
    parser.add_argument("--limit", type=int, default=25, help="Maximum number of files to label")
    parser.add_argument("--apply", action="store_true", help="Apply the label (default: dry run)")
    args = parser.parse_args()

    client = _client()
    label = _ensure_label(client, args.label, args.days)

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    stats = {"sites": 0, "files": 0, "labeled": 0, "errors": 0}

    for site in client.sites.get_all().execute_query():
        stats["sites"] += 1
        for drive in site.drives.get().execute_query():
            if any(token in (drive.name or "") for token in _SKIP_LIBRARIES):
                continue
            for item in drive.root.children.get().execute_query():
                if not item.file:
                    continue
                stats["files"] += 1
                created = item.created_datetime
                if created is None or created > cutoff:
                    continue
                try:
                    item.retention_label.get().execute_query()
                    if item.retention_label.name:
                        continue
                    where = f"{site.display_name} / {drive.name} / {item.name}"
                    if args.apply:
                        item.set_retention_label(label.display_name).execute_query()
                        stats["labeled"] += 1
                        print(f"  + {where}")
                    else:
                        print(f"  - {where}")
                    if stats["labeled"] >= args.limit:
                        break
                except Exception as exc:  # report the failure and keep scanning
                    stats["errors"] += 1
                    print(f"  ! {item.name}: {exc}")
            if stats["labeled"] >= args.limit:
                break

    verb = "Labeled" if args.apply else "Would label"
    print(f"\nSites: {stats['sites']}  Files: {stats['files']}  {verb}: {stats['labeled']}  Errors: {stats['errors']}")
    if not args.apply:
        print("Re-run with --apply to make the changes.")


if __name__ == "__main__":
    main()
