from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.unified_rbac_resource_action import (
        UnifiedRbacResourceAction,
    )


class UnifiedRbacResourceNamespace(Entity):
    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def resource_actions(self) -> EntityCollection[UnifiedRbacResourceAction]:
        """Gets the resourceActions property"""
        from office365.directory.unified_rbac_resource_action import (
            UnifiedRbacResourceAction,
        )

        return self.properties.get(
            "resourceActions",
            EntityCollection[UnifiedRbacResourceAction](
                self.context, UnifiedRbacResourceAction, ResourcePath("resourceActions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRbacResourceNamespace"
