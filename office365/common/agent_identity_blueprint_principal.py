from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import GuidCollection

if TYPE_CHECKING:
    from office365.directory.objects.object import DirectoryObject


class AgentIdentityBlueprintPrincipal(Entity):
    @property
    def manager_applications(self) -> GuidCollection:
        """Gets the managerApplications property"""
        return self.properties.get("managerApplications", GuidCollection())

    @property
    def sponsors(self) -> EntityCollection[DirectoryObject]:
        """Gets the sponsors property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "sponsors",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("sponsors", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AgentIdentityBlueprintPrincipal"
