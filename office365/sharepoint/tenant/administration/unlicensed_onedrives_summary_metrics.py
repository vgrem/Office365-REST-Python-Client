from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.sharepoint.tenant.administration.onedrives_summary_metrics_by_unlicensed_reason import (
    OneDrivesSummaryMetricsByUnlicensedReason,
)


@dataclass
class UnlicensedOneDrivesSummaryMetrics(ClientValue):
    agedOverThreshold: OneDrivesSummaryMetricsByUnlicensedReason = field(
        default_factory=OneDrivesSummaryMetricsByUnlicensedReason
    )
    all: OneDrivesSummaryMetricsByUnlicensedReason = field(default_factory=OneDrivesSummaryMetricsByUnlicensedReason)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.OdbMetricsAggregation.UnlicensedOneDrivesSummaryMetrics"
