from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.calls.ai_insight import CallAiInsight


class AiOnlineMeeting(Entity):
    @property
    def ai_insights(self) -> EntityCollection[CallAiInsight]:
        """Gets the aiInsights property"""
        from office365.communications.calls.ai_insight import CallAiInsight

        return self.properties.get(
            "aiInsights",
            EntityCollection[CallAiInsight](self.context, CallAiInsight, ResourcePath("aiInsights", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AiOnlineMeeting"
