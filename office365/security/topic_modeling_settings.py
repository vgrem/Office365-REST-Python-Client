from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class TopicModelingSettings(ClientValue):
    dynamicallyAdjustTopicCount: bool | None = None
    ignoreNumbers: bool | None = None
    isEnabled: bool | None = None
    topicCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.TopicModelingSettings"
