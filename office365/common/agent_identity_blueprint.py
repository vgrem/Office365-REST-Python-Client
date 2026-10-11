from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.inheritable_permission import InheritablePermission
    from office365.directory.objects.object import DirectoryObject


class AgentIdentityBlueprint(Entity):
    @property
    def inheritable_permissions(self) -> EntityCollection[InheritablePermission]:
        """Gets the inheritablePermissions property"""
        from office365.directory.inheritable_permission import InheritablePermission

        return self.properties.get(
            "inheritablePermissions",
            EntityCollection[InheritablePermission](
                self.context, InheritablePermission, ResourcePath("inheritablePermissions", self.resource_path)
            ),
        )

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
        return "microsoft.graph.AgentIdentityBlueprint"
