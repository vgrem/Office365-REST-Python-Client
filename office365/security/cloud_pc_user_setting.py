from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.virtualendpoint.cloudpcs.restorepointsetting import (
        CloudPcRestorePointSetting,
    )
    from office365.security.cloud_pc_user_setting_assignment import (
        CloudPcUserSettingAssignment,
    )


class CloudPcUserSetting(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def local_admin_enabled(self) -> Optional[bool]:
        """Gets the localAdminEnabled property"""
        return self.properties.get("localAdminEnabled", None)

    @property
    def reset_enabled(self) -> Optional[bool]:
        """Gets the resetEnabled property"""
        return self.properties.get("resetEnabled", None)

    @property
    def restore_point_setting(self) -> CloudPcRestorePointSetting:
        """Gets the restorePointSetting property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.restorepointsetting import (
            CloudPcRestorePointSetting,
        )

        return self.properties.get("restorePointSetting", CloudPcRestorePointSetting())

    @property
    def assignments(self) -> EntityCollection[CloudPcUserSettingAssignment]:
        """Gets the assignments property"""
        from office365.security.cloud_pc_user_setting_assignment import (
            CloudPcUserSettingAssignment,
        )

        return self.properties.get(
            "assignments",
            EntityCollection[CloudPcUserSettingAssignment](
                self.context, CloudPcUserSettingAssignment, ResourcePath("assignments", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudPcUserSetting"
