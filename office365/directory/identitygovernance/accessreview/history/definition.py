from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.accessreview.history.decisionfilter import (
    AccessReviewHistoryDecisionFilter,
)
from office365.directory.identitygovernance.accessreview.history.status import (
    AccessReviewHistoryStatus,
)
from office365.directory.identitygovernance.accessreview.history_instance import (
    AccessReviewHistoryInstance,
)
from office365.directory.identitygovernance.accessreview.scope import AccessReviewScope
from office365.directory.users.identity import UserIdentity
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.accessreview.history_schedule_settings import (
        AccessReviewHistoryScheduleSettings,
    )


class AccessReviewHistoryDefinition(Entity):
    """
    Represents a collection of access review historical data and the scopes used to collect that data.

    An accessReviewHistoryDefinition contains a list of accessReviewHistoryInstance objects.
    Each recurrence of the history definition creates an instance. In the case of a one-time history definition,
    only one instance is created.
    """

    @property
    def scopes(self):
        """
        Used to scope what reviews are included in the fetched history data. Fetches reviews whose scope matches with
        this provided scope. Required.
        """
        return self.properties.get("scopes", ClientValueCollection(AccessReviewScope))

    @property
    def created_by(self) -> UserIdentity:
        """Gets the createdBy property"""
        return self.properties.get("createdBy", UserIdentity())

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def decisions(self) -> ClientValueCollection[AccessReviewHistoryDecisionFilter]:
        """Gets the decisions property"""
        return self.properties.get(
            "decisions", ClientValueCollection[AccessReviewHistoryDecisionFilter](AccessReviewHistoryDecisionFilter)
        )

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def review_history_period_end_date_time(self) -> datetime:
        """Gets the reviewHistoryPeriodEndDateTime property"""
        return self.properties.get("reviewHistoryPeriodEndDateTime", datetime.min)

    @property
    def review_history_period_start_date_time(self) -> datetime:
        """Gets the reviewHistoryPeriodStartDateTime property"""
        return self.properties.get("reviewHistoryPeriodStartDateTime", datetime.min)

    @property
    def status(self) -> AccessReviewHistoryStatus:
        """Gets the status property"""
        return self.properties.get("status", AccessReviewHistoryStatus.done)

    @property
    def instances(self) -> EntityCollection[AccessReviewHistoryInstance]:
        """Gets the instances property"""
        return self.properties.get(
            "instances",
            EntityCollection[AccessReviewHistoryInstance](
                self.context, AccessReviewHistoryInstance, ResourcePath("instances", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewHistoryDefinition"

    @property
    def schedule_settings(self) -> AccessReviewHistoryScheduleSettings:
        """Gets the scheduleSettings property"""
        from office365.directory.identitygovernance.accessreview.history_schedule_settings import (
            AccessReviewHistoryScheduleSettings,
        )

        return self.properties.get("scheduleSettings", AccessReviewHistoryScheduleSettings())
