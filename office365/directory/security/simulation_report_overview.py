from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attacksimulations.event import TrainingEventsContent
from office365.directory.security.simulation_events_content import (
    SimulationEventsContent,
)
from office365.runtime.client_value import ClientValue


@dataclass
class SimulationReportOverview(ClientValue):
    resolvedTargetsCount: int | None = None
    simulationEventsContent: SimulationEventsContent = field(default_factory=SimulationEventsContent)
    trainingEventsContent: TrainingEventsContent = field(default_factory=TrainingEventsContent)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SimulationReportOverview"
