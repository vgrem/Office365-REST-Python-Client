from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.simulation_notification import SimulationNotification


@dataclass
class NoTrainingNotificationSetting(ClientValue):
    simulationNotification: SimulationNotification = field(default_factory=SimulationNotification)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.NoTrainingNotificationSetting"
