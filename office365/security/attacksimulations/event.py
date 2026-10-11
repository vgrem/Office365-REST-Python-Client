from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.assigned_training_info import AssignedTrainingInfo


@dataclass
class TrainingEventsContent(ClientValue):
    """"""

    trainingsAssignedUserCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TrainingEventsContent"

    assignedTrainingsInfos: ClientValueCollection[AssignedTrainingInfo] = field(
        default_factory=lambda: ClientValueCollection(AssignedTrainingInfo)
    )
