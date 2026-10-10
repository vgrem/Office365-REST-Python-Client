from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attacksimulations.users.details import (
    UserSimulationDetails,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class SimulationReport(ClientValue):
    simulationUsers: ClientValueCollection[UserSimulationDetails] = field(
        default_factory=lambda: ClientValueCollection(UserSimulationDetails)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SimulationReport"
