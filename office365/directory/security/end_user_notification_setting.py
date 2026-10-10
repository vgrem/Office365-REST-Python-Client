from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attacksimulations.endusernotificationpreference import (
    EndUserNotificationPreference,
)
from office365.directory.security.attacksimulations.endusernotificationsettingtype import (
    EndUserNotificationSettingType,
)
from office365.directory.security.positive_reinforcement_notification import (
    PositiveReinforcementNotification,
)
from office365.runtime.client_value import ClientValue


@dataclass
class EndUserNotificationSetting(ClientValue):
    notificationPreference: EndUserNotificationPreference = EndUserNotificationPreference.unknown
    positiveReinforcement: PositiveReinforcementNotification = field(default_factory=PositiveReinforcementNotification)
    settingType: EndUserNotificationSettingType = EndUserNotificationSettingType.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EndUserNotificationSetting"
