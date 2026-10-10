from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class StorageQuota(Entity):
    """ """

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.StorageQuota"

    @property
    def geo_allocated_storage_mb(self) -> Optional[int]:
        """Gets the GeoAllocatedStorageMB property"""
        return self.properties.get("GeoAllocatedStorageMB", None)

    @property
    def geo_available_storage_mb(self) -> Optional[int]:
        """Gets the GeoAvailableStorageMB property"""
        return self.properties.get("GeoAvailableStorageMB", None)

    @property
    def geo_location(self) -> Optional[str]:
        """Gets the GeoLocation property"""
        return self.properties.get("GeoLocation", None)

    @property
    def geo_used_archived_file_storage_mb(self) -> Optional[int]:
        """Gets the GeoUsedArchivedFileStorageMB property"""
        return self.properties.get("GeoUsedArchivedFileStorageMB", None)

    @property
    def geo_used_archive_storage_mb(self) -> Optional[int]:
        """Gets the GeoUsedArchiveStorageMB property"""
        return self.properties.get("GeoUsedArchiveStorageMB", None)

    @property
    def geo_used_storage_mb(self) -> Optional[int]:
        """Gets the GeoUsedStorageMB property"""
        return self.properties.get("GeoUsedStorageMB", None)

    @property
    def geo_used_version_size_storage_mb(self) -> Optional[int]:
        """Gets the GeoUsedVersionSizeStorageMB property"""
        return self.properties.get("GeoUsedVersionSizeStorageMB", None)

    @property
    def quota_type(self) -> Optional[int]:
        """Gets the QuotaType property"""
        return self.properties.get("QuotaType", None)

    @property
    def tenant_storage_mb(self) -> Optional[int]:
        """Gets the TenantStorageMB property"""
        return self.properties.get("TenantStorageMB", None)
