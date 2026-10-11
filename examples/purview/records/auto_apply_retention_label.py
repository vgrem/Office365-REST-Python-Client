"""
Auto-apply a retention label to unlabeled files across all SharePoint sites.

Lifecycle:
  1. Create a retention label
  2. Enumerate all SharePoint sites
  3. Scan each site's default document library for unlabeled files
  4. Apply the label to files within the retention window

Requires Global Administrator or Compliance Administrator role.
Requires delegated permissions:
  RecordsManagement.ReadWrite.All
  Sites.ReadWrite.All
"""

from datetime import datetime, timedelta

from office365.graph_client import GraphClient
from office365.security.labels.retention.actionafterretentionperiod import ActionAfterRetentionPeriod
from office365.security.labels.retention.behaviorduringretentionperiod import BehaviorDuringRetentionPeriod
from office365.security.labels.retention.defaultrecordbehavior import DefaultRecordBehavior
from office365.security.labels.retention.duration_in_days import RetentionDurationInDays
from office365.security.labels.retention.trigger import RetentionTrigger
from tests.settings import admin_username, client_id, tenant

LABEL_NAME = "Auto-Retain-365D"
RETENTION_DAYS = 365

client = (
    GraphClient(tenant=tenant)
    .with_token_interactive(client_id, admin_username)
    .require_role("Global Administrator", "Compliance Administrator")
)

label = client.security.labels.retention_labels.add(
    LABEL_NAME,
    RetentionTrigger.dateLabeled,
    RetentionDurationInDays(RETENTION_DAYS),
    BehaviorDuringRetentionPeriod.retainAsRecord,
    DefaultRecordBehavior.startLocked,
    ActionAfterRetentionPeriod.delete,
).execute_query()
print(f"Label created: {label.display_name}")

cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
stats = {"sites": 0, "files": 0, "labeled": 0, "errors": 0}

for site in client.sites.get_all().execute_query():
    stats["sites"] += 1
    for drive in site.drives.get().execute_query() or []:
        if any(x in (drive.name or "") for x in ["Preservation Hold", "Wiki Data", "App Catalog"]):
            continue
        for item in drive.root.children.get().execute_query() or []:
            stats["files"] += 1
            if not item.file:
                continue
            try:
                item.retention_label.get().execute_query()
                if item.retention_label.name:
                    continue
                created = item.created_datetime
                if created and created > cutoff:
                    item.set_retention_label(LABEL_NAME).execute_query()
                    stats["labeled"] += 1
                    print(f"  + {site.display_name} / {drive.name} / {item.name}")
                else:
                    print(f"  - {site.display_name} / {drive.name} / {item.name} (too old)")
            except Exception as e:
                stats["errors"] += 1
                print(f"  ! {site.display_name} / {drive.name} / {item.name} — {e}")

print(f"\nSites: {stats['sites']}  Files: {stats['files']}  Labeled: {stats['labeled']}  Errors: {stats['errors']}")
