from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class SPTenantIBPolicyComplianceReportEntityData(Entity):
    @property
    def update_one_drive_segments(self) -> Optional[bool]:
        """Gets the UpdateOneDriveSegments property"""
        return self.properties.get("UpdateOneDriveSegments", None)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.AuthPolicy.SPTenantIBPolicyComplianceReportEntityData"

    @property
    def update_onedrive_segments(self) -> Optional[bool]:
        """Gets the UpdateOneDriveSegments property"""
        return self.properties.get("UpdateOneDriveSegments", None)

    @property
    def update_user_owned_container_segments(self) -> Optional[bool]:
        """Gets the UpdateUserOwnedContainerSegments property"""
        return self.properties.get("UpdateUserOwnedContainerSegments", None)
