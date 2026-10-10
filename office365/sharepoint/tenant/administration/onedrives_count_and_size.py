from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class OneDrivesCountAndSize(ClientValue):
    count: int | None = None
    sizeBytes: float | None = None

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.OdbMetricsAggregation.OneDrivesCountAndSize"
