from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.security.attacksimulations.user import AttackSimulationUser
from office365.directory.security.user_training_event_info import UserTrainingEventInfo
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class UserSimulationDetails(ClientValue):
    """Represents a user of a tenant and their online actions in an attack simulation and training campaign.

    Args:
        assignedTrainingsCount (int): Number of trainings assigned to a user in an attack simulation and training
          campaign.
        simulationUser (AttackSimulationUser):
    """

    assignedTrainingsCount: int | None = None
    simulationUser: AttackSimulationUser = field(default_factory=AttackSimulationUser)

    completedTrainingsCount: int | None = None

    compromisedDateTime: datetime | None = None

    inProgressTrainingsCount: int | None = None

    isCompromised: bool | None = None

    reportedPhishDateTime: datetime | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserSimulationDetails"

    trainingEvents: ClientValueCollection[UserTrainingEventInfo] = field(
        default_factory=lambda: ClientValueCollection(UserTrainingEventInfo)
    )
