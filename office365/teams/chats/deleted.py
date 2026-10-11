from __future__ import annotations

from office365.entity import Entity


class DeletedChat(Entity):
    """Represents a chat that was deleted in Microsoft Teams."""

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeletedChat"
