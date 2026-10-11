from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.security.subjectrightsrequests.request import (
        SubjectRightsRequest,
    )


class Privacy(Entity):
    @property
    def subject_rights_requests(self) -> EntityCollection[SubjectRightsRequest]:
        """Gets the subjectRightsRequests property"""
        from office365.security.subjectrightsrequests.request import (
            SubjectRightsRequest,
        )

        return self.properties.get(
            "subjectRightsRequests",
            EntityCollection[SubjectRightsRequest](
                self.context, SubjectRightsRequest, ResourcePath("subjectRightsRequests", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Privacy"
