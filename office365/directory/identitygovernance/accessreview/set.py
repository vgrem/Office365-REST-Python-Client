from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.identitygovernance.accessreview.history.definition import (
    AccessReviewHistoryDefinition,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.identitygovernance.accessreview.schedule_definition import (
        AccessReviewScheduleDefinition,
    )
    from office365.directory.unified_root import UnifiedRoot


class AccessReviewSet(Entity):
    """
    Container for the base resources that expose the access reviews API and features. Currently exposes only the
    accessReviewScheduleDefinition relationship.
    """

    @odata(name="historyDefinitions")
    @property
    def history_definitions(self):
        """
        Represents a collection of access review history data and the scopes used to collect that data
        """
        return self.properties.get(
            "historyDefinitions",
            EntityCollection(
                self.context, AccessReviewHistoryDefinition, ResourcePath("historyDefinitions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewSet"

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
    def unified(self) -> UnifiedRoot:
        """Gets the unified property"""
        from office365.directory.unified_root import UnifiedRoot

        return self.properties.get("unified", UnifiedRoot(self.context, ResourcePath("unified", self.resource_path)))
