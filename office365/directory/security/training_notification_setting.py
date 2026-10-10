from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.base_end_user_notification import (
    BaseEndUserNotification,
)
from office365.directory.security.training_reminder_notification import (
    TrainingReminderNotification,
)
from office365.runtime.client_value import ClientValue


@dataclass
class TrainingNotificationSetting(ClientValue):
    trainingAssignment: BaseEndUserNotification = field(default_factory=BaseEndUserNotification)
    trainingReminder: TrainingReminderNotification = field(default_factory=TrainingReminderNotification)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TrainingNotificationSetting"
