from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attacksimulations.trainingstatus import TrainingStatus
from office365.directory.security.user_training_content_event_info import (
    UserTrainingContentEventInfo,
)
from office365.runtime.client_value import ClientValue


@dataclass
class UserTrainingEventInfo(ClientValue):
    displayName: str | None = None
    latestTrainingStatus: TrainingStatus = TrainingStatus.unknown
    trainingAssignedProperties: UserTrainingContentEventInfo = field(default_factory=UserTrainingContentEventInfo)
    trainingCompletedProperties: UserTrainingContentEventInfo = field(default_factory=UserTrainingContentEventInfo)
    trainingUpdatedProperties: UserTrainingContentEventInfo = field(default_factory=UserTrainingContentEventInfo)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserTrainingEventInfo"
