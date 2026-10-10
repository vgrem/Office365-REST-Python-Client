from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class LicensedOneDrivesSummaryMetrics(ClientValue):
    activePayAsYouGoCount: int | None = None
    maxedLicenseQuotaCount: int | None = None
    reachingStorageLimitCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.OdbMetricsAggregation.LicensedOneDrivesSummaryMetrics"
