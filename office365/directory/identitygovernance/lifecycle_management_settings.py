from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.emailsettings import EmailSettings
from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identitygovernance.quarantine_configuration import (
        QuarantineConfiguration,
    )


class LifecycleManagementSettings(Entity):
    @property
    def email_settings(self) -> EmailSettings:
        """Gets the emailSettings property"""
        return self.properties.get("emailSettings", EmailSettings())

    @property
    def workflow_schedule_interval_in_hours(self) -> Optional[int]:
        """Gets the workflowScheduleIntervalInHours property"""
        return self.properties.get("workflowScheduleIntervalInHours", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.LifecycleManagementSettings"

    @property
    def quarantine_configuration(self) -> QuarantineConfiguration:
        """Gets the quarantineConfiguration property"""
        from office365.directory.identitygovernance.quarantine_configuration import (
            QuarantineConfiguration,
        )

        return self.properties.get("quarantineConfiguration", QuarantineConfiguration())
