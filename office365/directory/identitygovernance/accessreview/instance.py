from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.accessreview.instance_decision_item import (
    AccessReviewInstanceDecisionItem,
)
from office365.directory.identitygovernance.accessreview.reviewer import (
    AccessReviewReviewer,
)
from office365.directory.identitygovernance.accessreview.scope import AccessReviewScope
from office365.directory.identitygovernance.accessreview.stages import (
    AccessReviewStageCollection,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.accessreview.error import (
        AccessReviewError,
    )
    from office365.directory.identitygovernance.accessreview.reviewer_scope import (
        AccessReviewReviewerScope,
    )


class AccessReviewInstance(Entity):
    """
    Represents a Microsoft Entra access review recurrence. If the parent accessReviewScheduleDefinition is a
    recurring access review, instances represent each recurrence. A review that does not recur will have exactly
    one instance. Instances also represent each unique group being reviewed in the schedule definition.
    If a schedule definition reviews multiple groups, each group will have a unique instance for each recurrence.

    Every accessReviewInstance contains a list of decisions that reviewers can take action on.
    There is one decision per identity being reviewed.
    """

    @property
    def stages(self) -> AccessReviewStageCollection:
        """If the instance has multiple stages, this returns the collection of stages.
        A new stage will only be created when the previous stage ends"""
        return self.properties.get(
            "stages", AccessReviewStageCollection(self.context, ResourcePath("stages", self.resource_path))
        )

    @property
    def end_date_time(self) -> datetime:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def scope(self) -> AccessReviewScope:
        """Gets the scope property"""
        return self.properties.get("scope", AccessReviewScope())

    @property
    def start_date_time(self) -> datetime:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def status(self) -> Optional[str]:
        """Gets the status property"""
        return self.properties.get("status", None)

    @property
    def contacted_reviewers(self) -> EntityCollection[AccessReviewReviewer]:
        """Gets the contactedReviewers property"""
        return self.properties.get(
            "contactedReviewers",
            EntityCollection[AccessReviewReviewer](
                self.context, AccessReviewReviewer, ResourcePath("contactedReviewers", self.resource_path)
            ),
        )

    @property
    def decisions(self) -> EntityCollection[AccessReviewInstanceDecisionItem]:
        """Gets the decisions property"""
        return self.properties.get(
            "decisions",
            EntityCollection[AccessReviewInstanceDecisionItem](
                self.context, AccessReviewInstanceDecisionItem, ResourcePath("decisions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewInstance"

    @property
    def errors(self) -> ClientValueCollection[AccessReviewError]:
        """Gets the errors property"""
        from office365.directory.identitygovernance.accessreview.error import (
            AccessReviewError,
        )

        return self.properties.get("errors", ClientValueCollection[AccessReviewError](AccessReviewError))

    @property
    def fallback_reviewers(self) -> ClientValueCollection[AccessReviewReviewerScope]:
        """Gets the fallbackReviewers property"""
        from office365.directory.identitygovernance.accessreview.reviewer_scope import (
            AccessReviewReviewerScope,
        )

        return self.properties.get(
            "fallbackReviewers", ClientValueCollection[AccessReviewReviewerScope](AccessReviewReviewerScope)
        )

    @property
    def reviewers(self) -> ClientValueCollection[AccessReviewReviewerScope]:
        """Gets the reviewers property"""
        from office365.directory.identitygovernance.accessreview.reviewer_scope import (
            AccessReviewReviewerScope,
        )

        return self.properties.get(
            "reviewers", ClientValueCollection[AccessReviewReviewerScope](AccessReviewReviewerScope)
        )
