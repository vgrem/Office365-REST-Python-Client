from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.m365_capability_resource_scopes import (
    M365CapabilityResourceScopes,
)
from office365.runtime.client_value import ClientValue


@dataclass
class M365CapabilityInboundAccess(ClientValue):
    isAllowed: bool | None = None
    resourceScopes: M365CapabilityResourceScopes = field(default_factory=M365CapabilityResourceScopes)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.M365CapabilityInboundAccess"
