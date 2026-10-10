from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity


class FileStatus(Entity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.FilePublish.Model.FileStatus"

    @property
    def error_code(self) -> Optional[int]:
        """Gets the ErrorCode property"""
        return self.properties.get("ErrorCode", None)

    @property
    def initial_creation(self) -> Optional[bool]:
        """Gets the InitialCreation property"""
        return self.properties.get("InitialCreation", None)

    @property
    def list_item_id(self) -> Optional[int]:
        """Gets the ListItemId property"""
        return self.properties.get("ListItemId", None)

    @property
    def parent_list_id(self) -> Optional[UUID]:
        """Gets the ParentListId property"""
        return self.properties.get("ParentListId", None)

    @property
    def path(self) -> ResourcePath:
        """Gets the Path property"""
        from office365.sharepoint.types.resource_path import ResourcePath

        return self.properties.get("Path", ResourcePath())

    @property
    def succeeded(self) -> Optional[bool]:
        """Gets the Succeeded property"""
        return self.properties.get("Succeeded", None)

    @property
    def unique_id(self) -> Optional[UUID]:
        """Gets the UniqueId property"""
        return self.properties.get("UniqueId", None)
