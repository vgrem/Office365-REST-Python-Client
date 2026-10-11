from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.virtualendpoint.cloudpcs.deviceimageerrorcode import (
        CloudPcDeviceImageErrorCode,
    )
    from office365.intune.devices.management.virtualendpoint.cloudpcs.deviceimageosstatus import (
        CloudPcDeviceImageOsStatus,
    )
    from office365.intune.devices.management.virtualendpoint.cloudpcs.deviceimagestatus import (
        CloudPcDeviceImageStatus,
    )


class CloudPcDeviceImage(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def error_code(self) -> CloudPcDeviceImageErrorCode:
        """Gets the errorCode property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.deviceimageerrorcode import (
            CloudPcDeviceImageErrorCode,
        )

        return self.properties.get("errorCode", CloudPcDeviceImageErrorCode.internalServerError)

    @property
    def expiration_date(self) -> Optional[date]:
        """Gets the expirationDate property"""
        return self.properties.get("expirationDate", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def operating_system(self) -> Optional[str]:
        """Gets the operatingSystem property"""
        return self.properties.get("operatingSystem", None)

    @property
    def os_build_number(self) -> Optional[str]:
        """Gets the osBuildNumber property"""
        return self.properties.get("osBuildNumber", None)

    @property
    def os_status(self) -> CloudPcDeviceImageOsStatus:
        """Gets the osStatus property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.deviceimageosstatus import (
            CloudPcDeviceImageOsStatus,
        )

        return self.properties.get("osStatus", CloudPcDeviceImageOsStatus.supported)

    @property
    def os_version_number(self) -> Optional[str]:
        """Gets the osVersionNumber property"""
        return self.properties.get("osVersionNumber", None)

    @property
    def size_in_gb(self) -> Optional[int]:
        """Gets the sizeInGB property"""
        return self.properties.get("sizeInGB", None)

    @property
    def source_image_resource_id(self) -> Optional[str]:
        """Gets the sourceImageResourceId property"""
        return self.properties.get("sourceImageResourceId", None)

    @property
    def status(self) -> CloudPcDeviceImageStatus:
        """Gets the status property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.deviceimagestatus import (
            CloudPcDeviceImageStatus,
        )

        return self.properties.get("status", CloudPcDeviceImageStatus.pending)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudPcDeviceImage"
