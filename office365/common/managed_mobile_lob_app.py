from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.content import MobileAppContent


class ManagedMobileLobApp(Entity):
    @property
    def committed_content_version(self) -> Optional[str]:
        """Gets the committedContentVersion property"""
        return self.properties.get("committedContentVersion", None)

    @property
    def file_name(self) -> Optional[str]:
        """Gets the fileName property"""
        return self.properties.get("fileName", None)

    @property
    def size(self) -> Optional[int]:
        """Gets the size property"""
        return self.properties.get("size", None)

    @property
    def content_versions(self) -> EntityCollection[MobileAppContent]:
        """Gets the contentVersions property"""
        from office365.intune.devices.management.mobileapps.content import (
            MobileAppContent,
        )

        return self.properties.get(
            "contentVersions",
            EntityCollection[MobileAppContent](
                self.context, MobileAppContent, ResourcePath("contentVersions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedMobileLobApp"
