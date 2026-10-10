from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.sharepoint.tenant.administration.onedrives_count_and_size import (
    OneDrivesCountAndSize,
)


@dataclass
class OwnerNotInEntraOneDrivesSummaryMetrics(ClientValue):
    adminLocked: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)
    complianceHold: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)
    restoredSite: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)
    retentionPeriod: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)
    total: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)
    unknown: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.OdbMetricsAggregation.OwnerNotInEntraOneDrivesSummaryMetrics"  # noqa: E501
