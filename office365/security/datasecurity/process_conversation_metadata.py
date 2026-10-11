from __future__ import annotations

from dataclasses import dataclass, field

from office365.copilot.ai_agent_info import AiAgentInfo
from office365.copilot.ai_interaction_plugin import AiInteractionPlugin
from office365.directory.identitygovernance.resource_access_detail import ResourceAccessDetail
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection


@dataclass
class ProcessConversationMetadata(ClientValue):
    accessedResources: StringCollection = field(default_factory=StringCollection)
    accessedResources_v2: ClientValueCollection[ResourceAccessDetail] = field(
        default_factory=lambda: ClientValueCollection(ResourceAccessDetail)
    )
    agents: ClientValueCollection[AiAgentInfo] = field(default_factory=lambda: ClientValueCollection(AiAgentInfo))
    parentMessageId: str | None = None
    plugins: ClientValueCollection[AiInteractionPlugin] = field(
        default_factory=lambda: ClientValueCollection(AiInteractionPlugin)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProcessConversationMetadata"
