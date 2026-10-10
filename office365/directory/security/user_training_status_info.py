from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.directory.security.attacksimulations.trainingstatus import TrainingStatus
from office365.runtime.client_value import ClientValue


@dataclass
class UserTrainingStatusInfo(ClientValue):
    assignedDateTime: datetime | None = None
    completionDateTime: datetime | None = None
    displayName: str | None = None
    trainingStatus: TrainingStatus = TrainingStatus.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserTrainingStatusInfo"
