from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.datasecurity.policy_binding import PolicyBinding


@dataclass
class PolicyTenantScope(ClientValue):
    policyScope: PolicyBinding = field(default_factory=PolicyBinding)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PolicyTenantScope"
