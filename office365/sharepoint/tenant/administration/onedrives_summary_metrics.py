from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.sharepoint.tenant.administration.licensed_onedrives_summary_metrics import (
    LicensedOneDrivesSummaryMetrics,
)
from office365.sharepoint.tenant.administration.unlicensed_onedrives_summary_metrics import (
    UnlicensedOneDrivesSummaryMetrics,
)


@dataclass
class OneDrivesSummaryMetrics(ClientValue):
    calculatedOn: datetime | None = None
    licensed: LicensedOneDrivesSummaryMetrics = field(default_factory=LicensedOneDrivesSummaryMetrics)
    unlicensed: UnlicensedOneDrivesSummaryMetrics = field(default_factory=UnlicensedOneDrivesSummaryMetrics)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.OdbMetricsAggregation.OneDrivesSummaryMetrics"
