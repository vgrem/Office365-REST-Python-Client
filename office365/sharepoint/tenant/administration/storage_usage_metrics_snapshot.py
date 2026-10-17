from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class StorageUsageMetricsSnapshot(ClientValue):
    ActiveSitesCount: int | None = None
    ActiveUsedStorageMB: int | None = None
    AllocationType: int | None = None
    ArchivedFilesUsedStorageMB: int | None = None
    ArchivedSitesCount: int | None = None
    ArchivedSitesUsedStorageMB: int | None = None
    AvailableFreeStorageMB: int | None = None
    GeoLocations: StringCollection = field(default_factory=StringCollection)
    MetricsAggregationScope: int | None = None
    SnapshotDate: datetime | None = field(default_factory=lambda: datetime.min)
    TotalAvailableStorageMB: int | None = None
    VersionsUsedStorageMB: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.TenantAdmin.StorageUsage.StorageUsageMetricsSnapshot"

    IsArchiveStorageReclassifiedAsActive: bool | None = None

    PaygoActiveStorageMB: int | None = None

    PaygoArchiveStorageMB: int | None = None
