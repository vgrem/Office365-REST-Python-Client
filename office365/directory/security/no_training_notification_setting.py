from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.simulation_notification import SimulationNotification
from office365.runtime.client_value import ClientValue


@dataclass
class NoTrainingNotificationSetting(ClientValue):
    simulationNotification: SimulationNotification = field(default_factory=SimulationNotification)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.NoTrainingNotificationSetting"
