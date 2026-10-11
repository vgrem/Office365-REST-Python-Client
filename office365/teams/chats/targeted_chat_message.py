from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.permissions.identity import Identity


class TargetedChatMessage(Entity):
    @property
    def recipient(self) -> Identity:
        """Gets the recipient property"""
        from office365.directory.permissions.identity import Identity

        return self.properties.get("recipient", Identity())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TargetedChatMessage"
