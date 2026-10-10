from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attacksimulations.user import AttackSimulationUser
from office365.runtime.client_value import ClientValue


@dataclass
class AttackSimulationRepeatOffender(ClientValue):
    """
        Represents a user in a tenant who has given way to attacks more than once across various attack simulation
    and training campaigns.
    """

    attackSimulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)
    repeatOffenceCount: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationRepeatOffender"
