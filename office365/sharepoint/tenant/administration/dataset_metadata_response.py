from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.tenant.administration.dataset_metadata_info import (
    DatasetMetadataInfo,
)


@dataclass
class DatasetMetadataResponse(ClientValue):
    featureId: str | None = None
    sitePermissions: ClientValueCollection[DatasetMetadataInfo] = field(
        default_factory=lambda: ClientValueCollection(DatasetMetadataInfo)
    )
    TenantAdminSiteLifeCycle: ClientValueCollection[DatasetMetadataInfo] = field(
        default_factory=lambda: ClientValueCollection(DatasetMetadataInfo)
    )
    catalogManagement: ClientValueCollection[DatasetMetadataInfo] = field(
        default_factory=lambda: ClientValueCollection(DatasetMetadataInfo)
    )
    siteStorageDetails: ClientValueCollection[DatasetMetadataInfo] = field(
        default_factory=lambda: ClientValueCollection(DatasetMetadataInfo)
    )

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.SPOAdminReportInsights.Models.DatasetMetadataResponse"

    appIntelligence: ClientValueCollection[DatasetMetadataInfo] = field(
        default_factory=lambda: ClientValueCollection(DatasetMetadataInfo)
    )
