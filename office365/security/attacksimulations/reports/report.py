from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.attacksimulations.reports.overview import (
    SimulationReportOverview,
)
from office365.security.attacksimulations.users.details import (
    UserSimulationDetails,
)


@dataclass
class SimulationReport(ClientValue):
    """
    Represents a report of an attack simulation and training campaign, including an overview and users who
    participated in the campaign.
    """

    overview: SimulationReportOverview = field(default_factory=SimulationReportOverview)
    simulationUsers: ClientValueCollection[UserSimulationDetails] = field(
        default_factory=lambda: ClientValueCollection(UserSimulationDetails)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SimulationReport"
