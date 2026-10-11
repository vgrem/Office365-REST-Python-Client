from __future__ import annotations

from enum import Enum


class AiAgentPlatform(Enum):
    unknown = "0"
    azureAIFoundry = "10"
    copilotStudio = "20"
    copilot = "30"
    unknownFutureValue = "40"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AiAgentPlatform"
