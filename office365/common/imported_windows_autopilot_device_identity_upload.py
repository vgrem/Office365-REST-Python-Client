from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.imported_windows_autopilot_device_identity_upload_status import (
        ImportedWindowsAutopilotDeviceIdentityUploadStatus,
    )
    from office365.intune.devices.management.imported_windows_autopilot_device_identity import (
        ImportedWindowsAutopilotDeviceIdentity,
    )


class ImportedWindowsAutopilotDeviceIdentityUpload(Entity):
    @property
    def created_date_time_utc(self) -> Optional[datetime]:
        """Gets the createdDateTimeUtc property"""
        return self.properties.get("createdDateTimeUtc", datetime.min)

    @property
    def status(self) -> ImportedWindowsAutopilotDeviceIdentityUploadStatus:
        """Gets the status property"""
        from office365.intune.devices.imported_windows_autopilot_device_identity_upload_status import (
            ImportedWindowsAutopilotDeviceIdentityUploadStatus,
        )

        return self.properties.get("status", ImportedWindowsAutopilotDeviceIdentityUploadStatus.noUpload)

    @property
    def device_identities(self) -> EntityCollection[ImportedWindowsAutopilotDeviceIdentity]:
        """Gets the deviceIdentities property"""
        from office365.intune.devices.management.imported_windows_autopilot_device_identity import (
            ImportedWindowsAutopilotDeviceIdentity,
        )

        return self.properties.get(
            "deviceIdentities",
            EntityCollection[ImportedWindowsAutopilotDeviceIdentity](
                self.context,
                ImportedWindowsAutopilotDeviceIdentity,
                ResourcePath("deviceIdentities", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ImportedWindowsAutopilotDeviceIdentityUpload"
