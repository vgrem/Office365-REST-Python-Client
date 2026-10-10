from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.directory.security.attacksimulations.trainingcompletionduration import (
    TrainingCompletionDuration,
)
from office365.runtime.client_value import ClientValue


@dataclass
class MicrosoftManagedTrainingSetting(ClientValue):
    completionDateTime: datetime | None = None
    trainingCompletionDuration: TrainingCompletionDuration = TrainingCompletionDuration.week

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MicrosoftManagedTrainingSetting"
