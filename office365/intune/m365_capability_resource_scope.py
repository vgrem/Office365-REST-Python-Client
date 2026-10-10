from __future__ import annotations

from dataclasses import dataclass

from office365.intune.m365_resource_type import M365ResourceType
from office365.runtime.client_value import ClientValue


@dataclass
class M365CapabilityResourceScope(ClientValue):
    resourceId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.M365CapabilityResourceScope"

    resourceType: M365ResourceType = M365ResourceType.none
