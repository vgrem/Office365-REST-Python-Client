from __future__ import annotations

from typing import Optional

from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class GroupCreationParams(Entity):
    @property
    def classification(self) -> Optional[str]:
        """Gets the Classification property"""
        return self.properties.get("Classification", None)

    @property
    def creation_options(self) -> StringCollection:
        """Gets the CreationOptions property"""
        return self.properties.get("CreationOptions", StringCollection())

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def owners(self) -> StringCollection:
        """Gets the Owners property"""
        return self.properties.get("Owners", StringCollection())

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantManagement.GroupCreationParams"
