from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.attacksimulations.trainingsettingtype import (
    TrainingSettingType,
)


@dataclass
class TrainingSetting(ClientValue):
    settingType: TrainingSettingType = TrainingSettingType.microsoftCustom

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TrainingSetting"
