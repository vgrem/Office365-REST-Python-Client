from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.attacksimulations.trainingcompletionduration import (
    TrainingCompletionDuration,
)
from office365.security.microsoft_training_assignment_mapping import (
    MicrosoftTrainingAssignmentMapping,
)


@dataclass
class MicrosoftCustomTrainingSetting(ClientValue):
    completionDateTime: datetime | None = None
    trainingAssignmentMappings: ClientValueCollection[MicrosoftTrainingAssignmentMapping] = field(
        default_factory=lambda: ClientValueCollection(MicrosoftTrainingAssignmentMapping)
    )
    trainingCompletionDuration: TrainingCompletionDuration = TrainingCompletionDuration.week

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MicrosoftCustomTrainingSetting"
