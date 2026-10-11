from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.base_end_user_notification import (
    BaseEndUserNotification,
)
from office365.security.training_reminder_notification import (
    TrainingReminderNotification,
)


@dataclass
class TrainingNotificationSetting(ClientValue):
    trainingAssignment: BaseEndUserNotification = field(default_factory=BaseEndUserNotification)
    trainingReminder: TrainingReminderNotification = field(default_factory=TrainingReminderNotification)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TrainingNotificationSetting"
