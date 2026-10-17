from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class SPOM365AgentInsightsTop20AgentsDetails(ClientValue):
    AgentName: str | None = None
    AgentType: str | None = None
    RequestVolume: int | None = None
    SitesAccessed: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOM365AgentInsightsTop20AgentsDetails"

    IncludeOperations: bool | None = None

    Operations: str | None = None

    AgentPlatform: str | None = None

    IncludeAgentPlatform: bool | None = None
