from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.accessreview.instance import (
        AccessReviewInstance,
    )
    from office365.directory.identitygovernance.accessreview.instance_decision_item import (
        AccessReviewInstanceDecisionItem,
    )
    from office365.directory.identitygovernance.accessreview.schedule_definition import (
        AccessReviewScheduleDefinition,
    )


class UnifiedRoot(Entity):
    @property
    def decisions(self) -> EntityCollection[AccessReviewInstanceDecisionItem]:
        """Gets the decisions property"""
        from office365.directory.identitygovernance.accessreview.instance_decision_item import (
            AccessReviewInstanceDecisionItem,
        )

        return self.properties.get(
            "decisions",
            EntityCollection[AccessReviewInstanceDecisionItem](
                self.context, AccessReviewInstanceDecisionItem, ResourcePath("decisions", self.resource_path)
            ),
        )

    @property
    def definitions(self) -> EntityCollection[AccessReviewScheduleDefinition]:
        """Gets the definitions property"""
        from office365.directory.identitygovernance.accessreview.schedule_definition import (
            AccessReviewScheduleDefinition,
        )

        return self.properties.get(
            "definitions",
            EntityCollection[AccessReviewScheduleDefinition](
                self.context, AccessReviewScheduleDefinition, ResourcePath("definitions", self.resource_path)
            ),
        )

    @property
    def instances(self) -> EntityCollection[AccessReviewInstance]:
        """Gets the instances property"""
        from office365.directory.identitygovernance.accessreview.instance import (
            AccessReviewInstance,
        )

        return self.properties.get(
            "instances",
            EntityCollection[AccessReviewInstance](
                self.context, AccessReviewInstance, ResourcePath("instances", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoot"
