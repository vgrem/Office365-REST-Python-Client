from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.attacksimulations.trainingstatus import TrainingStatus


@dataclass
class UserTrainingStatusInfo(ClientValue):
    assignedDateTime: datetime | None = None
    completionDateTime: datetime | None = None
    displayName: str | None = None
    trainingStatus: TrainingStatus = TrainingStatus.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserTrainingStatusInfo"
