from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class EngagementConversationQuestionMessage(Entity):
    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EngagementConversationQuestionMessage"
