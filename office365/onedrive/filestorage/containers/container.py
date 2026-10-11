from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from typing_extensions import Self

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.groups.assigned_label import AssignedLabel
    from office365.onedrive.columns.definition import ColumnDefinition
    from office365.onedrive.drives.drive import Drive
    from office365.onedrive.filestorage.containers.custom_property_dictionary import (
        FileStorageContainerCustomPropertyDictionary,
    )
    from office365.onedrive.filestorage.containers.settings import (
        FileStorageContainerSettings,
    )
    from office365.onedrive.filestorage.containers.status import (
        FileStorageContainerStatus,
    )
    from office365.onedrive.filestorage.containers.viewpoint import (
        FileStorageContainerViewpoint,
    )
    from office365.onedrive.filestorage.sitelockstate import SiteLockState
    from office365.onedrive.permissions.permission import Permission
    from office365.onedrive.recyclebin.recyclebin import RecycleBin
    from office365.onedrive.sharepoint.group import SharePointGroup
    from office365.onedrive.sharepoint.migration.migration_job import (
        SharePointMigrationJob,
    )


class FileStorageContainer(Entity):
    """Represents a location where multiple users or a group of users can store files and access them
    via an application. All file system objects in a fileStorageContainer are returned as driveItem resources.
    """

    def activate(self) -> Self:
        """Activate a fileStorageContainer object.

        A container created in inactive state must be activated within 24 hours,
        or it will be automatically deleted. Upon activation, the status property
        changes from inactive to active.
        """
        qry = ServiceOperationQuery(self, "activate")
        self.context.add_query(qry)
        return self

    @odata(name="createdDateTime")
    @property
    def created_datetime(self) -> Optional[datetime]:
        """Date and time of the fileStorageContainer creation. Read-only."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "graph.fileStorageContainer"

    @property
    def assigned_sensitivity_label(self) -> AssignedLabel:
        """Gets the assignedSensitivityLabel property"""
        from office365.directory.groups.assigned_label import AssignedLabel

        return self.properties.get("assignedSensitivityLabel", AssignedLabel())

    @property
    def container_type_id(self) -> Optional[UUID]:
        """Gets the containerTypeId property"""
        return self.properties.get("containerTypeId", None)

    @property
    def custom_properties(self) -> FileStorageContainerCustomPropertyDictionary:
        """Gets the customProperties property"""
        from office365.onedrive.filestorage.containers.custom_property_dictionary import (
            FileStorageContainerCustomPropertyDictionary,
        )

        return self.properties.get("customProperties", FileStorageContainerCustomPropertyDictionary())

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def lock_state(self) -> SiteLockState:
        """Gets the lockState property"""
        from office365.onedrive.filestorage.sitelockstate import SiteLockState

        return self.properties.get("lockState", SiteLockState.unlocked)

    @property
    def settings(self) -> FileStorageContainerSettings:
        """Gets the settings property"""
        from office365.onedrive.filestorage.containers.settings import (
            FileStorageContainerSettings,
        )

        return self.properties.get("settings", FileStorageContainerSettings())

    @property
    def status(self) -> FileStorageContainerStatus:
        """Gets the status property"""
        from office365.onedrive.filestorage.containers.status import (
            FileStorageContainerStatus,
        )

        return self.properties.get("status", FileStorageContainerStatus.inactive)

    @property
    def viewpoint(self) -> FileStorageContainerViewpoint:
        """Gets the viewpoint property"""
        from office365.onedrive.filestorage.containers.viewpoint import (
            FileStorageContainerViewpoint,
        )

        return self.properties.get("viewpoint", FileStorageContainerViewpoint())

    @property
    def columns(self) -> EntityCollection[ColumnDefinition]:
        """Gets the columns property"""
        from office365.onedrive.columns.definition import ColumnDefinition

        return self.properties.get(
            "columns",
            EntityCollection[ColumnDefinition](
                self.context, ColumnDefinition, ResourcePath("columns", self.resource_path)
            ),
        )

    @property
    def drive(self) -> Drive:
        """Gets the drive property"""
        from office365.onedrive.drives.drive import Drive

        return self.properties.get("drive", Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def migration_jobs(self) -> EntityCollection[SharePointMigrationJob]:
        """Gets the migrationJobs property"""
        from office365.onedrive.sharepoint.migration.migration_job import (
            SharePointMigrationJob,
        )

        return self.properties.get(
            "migrationJobs",
            EntityCollection[SharePointMigrationJob](
                self.context, SharePointMigrationJob, ResourcePath("migrationJobs", self.resource_path)
            ),
        )

    @property
    def permissions(self) -> EntityCollection[Permission]:
        """Gets the permissions property"""
        from office365.onedrive.permissions.permission import Permission

        return self.properties.get(
            "permissions",
            EntityCollection[Permission](self.context, Permission, ResourcePath("permissions", self.resource_path)),
        )

    @property
    def recycle_bin(self) -> RecycleBin:
        """Gets the recycleBin property"""
        from office365.onedrive.recyclebin.recyclebin import RecycleBin

        return self.properties.get(
            "recycleBin", RecycleBin(self.context, ResourcePath("recycleBin", self.resource_path))
        )

    @property
    def sharepoint_groups(self) -> EntityCollection[SharePointGroup]:
        """Gets the sharePointGroups property"""
        from office365.onedrive.sharepoint.group import SharePointGroup

        return self.properties.get(
            "sharePointGroups",
            EntityCollection[SharePointGroup](
                self.context, SharePointGroup, ResourcePath("sharePointGroups", self.resource_path)
            ),
        )
