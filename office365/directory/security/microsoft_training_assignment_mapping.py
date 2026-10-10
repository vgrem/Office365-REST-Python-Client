from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attacksimulations.trainingassignedto import (
    TrainingAssignedTo,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class MicrosoftTrainingAssignmentMapping(ClientValue):
    assignedTo: ClientValueCollection[TrainingAssignedTo] = field(
        default_factory=lambda: ClientValueCollection(TrainingAssignedTo)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MicrosoftTrainingAssignmentMapping"
