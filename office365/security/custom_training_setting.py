from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.attacksimulations.trainingassignedto import (
    TrainingAssignedTo,
)


@dataclass
class CustomTrainingSetting(ClientValue):
    assignedTo: ClientValueCollection[TrainingAssignedTo] = field(
        default_factory=lambda: ClientValueCollection(TrainingAssignedTo)
    )
    description: str | None = None
    displayName: str | None = None
    durationInMinutes: int | None = None
    url: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomTrainingSetting"
