from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.recovery.job_filtering_criteria_base import (
        RecoveryJobFilteringCriteriaBase,
    )
    from office365.directory.recovery.recovery_status import RecoveryStatus


class RecoveryJobBase(Entity):
    @property
    def filtering_criteria(self) -> RecoveryJobFilteringCriteriaBase:
        """Gets the filteringCriteria property"""
        from office365.directory.recovery.job_filtering_criteria_base import (
            RecoveryJobFilteringCriteriaBase,
        )

        return self.properties.get("filteringCriteria", RecoveryJobFilteringCriteriaBase())

    @property
    def job_completion_date_time(self) -> Optional[datetime]:
        """Gets the jobCompletionDateTime property"""
        return self.properties.get("jobCompletionDateTime", datetime.min)

    @property
    def job_start_date_time(self) -> Optional[datetime]:
        """Gets the jobStartDateTime property"""
        return self.properties.get("jobStartDateTime", datetime.min)

    @property
    def status(self) -> RecoveryStatus:
        """Gets the status property"""
        from office365.directory.recovery.recovery_status import RecoveryStatus

        return self.properties.get("status", RecoveryStatus.initialized)

    @property
    def target_state_date_time(self) -> Optional[datetime]:
        """Gets the targetStateDateTime property"""
        return self.properties.get("targetStateDateTime", datetime.min)

    @property
    def total_changed_links_calculated(self) -> Optional[int]:
        """Gets the totalChangedLinksCalculated property"""
        return self.properties.get("totalChangedLinksCalculated", None)

    @property
    def total_changed_objects_calculated(self) -> Optional[int]:
        """Gets the totalChangedObjectsCalculated property"""
        return self.properties.get("totalChangedObjectsCalculated", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.entraRecoveryServices.RecoveryJobBase"
