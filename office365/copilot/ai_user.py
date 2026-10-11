from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.copilot.ai_interaction_history import AiInteractionHistory
    from office365.copilot.ai_online_meeting import AiOnlineMeeting


class AiUser(Entity):
    @property
    def interaction_history(self) -> AiInteractionHistory:
        """Gets the interactionHistory property"""
        from office365.copilot.ai_interaction_history import AiInteractionHistory

        return self.properties.get(
            "interactionHistory",
            AiInteractionHistory(self.context, ResourcePath("interactionHistory", self.resource_path)),
        )

    @property
    def online_meetings(self) -> EntityCollection[AiOnlineMeeting]:
        """Gets the onlineMeetings property"""
        from office365.copilot.ai_online_meeting import AiOnlineMeeting

        return self.properties.get(
            "onlineMeetings",
            EntityCollection[AiOnlineMeeting](
                self.context, AiOnlineMeeting, ResourcePath("onlineMeetings", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AiUser"
