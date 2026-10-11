from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.engagement_role_member import EngagementRoleMember


class EngagementRole(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def members(self) -> EntityCollection[EngagementRoleMember]:
        """Gets the members property"""
        from office365.common.engagement_role_member import EngagementRoleMember

        return self.properties.get(
            "members",
            EntityCollection[EngagementRoleMember](
                self.context, EngagementRoleMember, ResourcePath("members", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EngagementRole"
