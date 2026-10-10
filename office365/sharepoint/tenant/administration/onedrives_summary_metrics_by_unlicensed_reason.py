from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.sharepoint.tenant.administration.onedrives_count_and_size import (
    OneDrivesCountAndSize,
)
from office365.sharepoint.tenant.administration.owner_not_in_entra_onedrives_summary_metrics import (
    OwnerNotInEntraOneDrivesSummaryMetrics,
)


@dataclass
class OneDrivesSummaryMetricsByUnlicensedReason(ClientValue):
    activeUsersWithoutLicense: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)
    duplicateOfLicensedUser: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)
    ownerNotInEntra: OwnerNotInEntraOneDrivesSummaryMetrics = field(
        default_factory=OwnerNotInEntraOneDrivesSummaryMetrics
    )
    total: OneDrivesCountAndSize = field(default_factory=OneDrivesCountAndSize)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.OdbMetricsAggregation.OneDrivesSummaryMetricsByUnlicensedReason"  # noqa: E501
