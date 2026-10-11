from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.m365_capability_resource_scope import (
    M365CapabilityResourceScope,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class M365CapabilityResourceScopes(ClientValue):
    excluded: ClientValueCollection[M365CapabilityResourceScope] = field(
        default_factory=lambda: ClientValueCollection(M365CapabilityResourceScope)
    )
    included: ClientValueCollection[M365CapabilityResourceScope] = field(
        default_factory=lambda: ClientValueCollection(M365CapabilityResourceScope)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.M365CapabilityResourceScopes"
