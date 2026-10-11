from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.virtualendpoint.cloudpcs.galleryimagestatus import (
        CloudPcGalleryImageStatus,
    )


class CloudPcGalleryImage(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def end_date(self) -> Optional[date]:
        """Gets the endDate property"""
        return self.properties.get("endDate", None)

    @property
    def expiration_date(self) -> Optional[date]:
        """Gets the expirationDate property"""
        return self.properties.get("expirationDate", None)

    @property
    def offer_name(self) -> Optional[str]:
        """Gets the offerName property"""
        return self.properties.get("offerName", None)

    @property
    def os_version_number(self) -> Optional[str]:
        """Gets the osVersionNumber property"""
        return self.properties.get("osVersionNumber", None)

    @property
    def publisher_name(self) -> Optional[str]:
        """Gets the publisherName property"""
        return self.properties.get("publisherName", None)

    @property
    def size_in_gb(self) -> Optional[int]:
        """Gets the sizeInGB property"""
        return self.properties.get("sizeInGB", None)

    @property
    def sku_name(self) -> Optional[str]:
        """Gets the skuName property"""
        return self.properties.get("skuName", None)

    @property
    def start_date(self) -> Optional[date]:
        """Gets the startDate property"""
        return self.properties.get("startDate", None)

    @property
    def status(self) -> CloudPcGalleryImageStatus:
        """Gets the status property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.galleryimagestatus import (
            CloudPcGalleryImageStatus,
        )

        return self.properties.get("status", CloudPcGalleryImageStatus.supported)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudPcGalleryImage"
