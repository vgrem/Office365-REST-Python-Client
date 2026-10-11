from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.ai_agent_platform import AiAgentPlatform


@dataclass
class AiAgentEvidence(ClientValue):
    agentId: str | None = None
    agentName: str | None = None
    instructions: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AiAgentEvidence"

    hostingPlatformType: AiAgentPlatform = AiAgentPlatform.unknown
