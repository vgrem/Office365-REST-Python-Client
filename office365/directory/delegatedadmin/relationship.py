from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.delegatedadmin.access_assignment import (
        DelegatedAdminAccessAssignment,
    )
    from office365.directory.delegatedadmin.access_details import (
        DelegatedAdminAccessDetails,
    )
    from office365.directory.delegatedadmin.relationship_customer_participant import (
        DelegatedAdminRelationshipCustomerParticipant,
    )
    from office365.directory.delegatedadmin.relationship_operation import (
        DelegatedAdminRelationshipOperation,
    )
    from office365.directory.delegatedadmin.relationship_request import (
        DelegatedAdminRelationshipRequest,
    )
    from office365.directory.delegatedadmin.relationshipstatus import (
        DelegatedAdminRelationshipStatus,
    )
    from office365.runtime.types.duration import timedelta


class DelegatedAdminRelationship(Entity):
    """Represents a delegated admin relationship between a partner and customer."""

    @property
    def access_details(self) -> DelegatedAdminAccessDetails:
        """Gets the accessDetails property"""
        from office365.directory.delegatedadmin.access_details import (
            DelegatedAdminAccessDetails,
        )

        return self.properties.get("accessDetails", DelegatedAdminAccessDetails())

    @property
    def activated_date_time(self) -> Optional[datetime]:
        """Gets the activatedDateTime property"""
        return self.properties.get("activatedDateTime", datetime.min)

    @property
    def auto_extend_duration(self) -> Optional[timedelta]:
        """Gets the autoExtendDuration property"""
        return self.properties.get("autoExtendDuration", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def customer(self) -> DelegatedAdminRelationshipCustomerParticipant:
        """Gets the customer property"""
        from office365.directory.delegatedadmin.relationship_customer_participant import (
            DelegatedAdminRelationshipCustomerParticipant,
        )

        return self.properties.get("customer", DelegatedAdminRelationshipCustomerParticipant())

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def duration(self) -> Optional[timedelta]:
        """Gets the duration property"""
        return self.properties.get("duration", None)

    @property
    def end_date_time(self) -> Optional[datetime]:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def status(self) -> DelegatedAdminRelationshipStatus:
        """Gets the status property"""
        from office365.directory.delegatedadmin.relationshipstatus import (
            DelegatedAdminRelationshipStatus,
        )

        return self.properties.get("status", DelegatedAdminRelationshipStatus.activating)

    @property
    def access_assignments(self) -> EntityCollection[DelegatedAdminAccessAssignment]:
        """Gets the accessAssignments property"""
        from office365.directory.delegatedadmin.access_assignment import (
            DelegatedAdminAccessAssignment,
        )

        return self.properties.get(
            "accessAssignments",
            EntityCollection[DelegatedAdminAccessAssignment](
                self.context, DelegatedAdminAccessAssignment, ResourcePath("accessAssignments", self.resource_path)
            ),
        )

    @property
    def operations(self) -> EntityCollection[DelegatedAdminRelationshipOperation]:
        """Gets the operations property"""
        from office365.directory.delegatedadmin.relationship_operation import (
            DelegatedAdminRelationshipOperation,
        )

        return self.properties.get(
            "operations",
            EntityCollection[DelegatedAdminRelationshipOperation](
                self.context, DelegatedAdminRelationshipOperation, ResourcePath("operations", self.resource_path)
            ),
        )

    @property
    def requests(self) -> EntityCollection[DelegatedAdminRelationshipRequest]:
        """Gets the requests property"""
        from office365.directory.delegatedadmin.relationship_request import (
            DelegatedAdminRelationshipRequest,
        )

        return self.properties.get(
            "requests",
            EntityCollection[DelegatedAdminRelationshipRequest](
                self.context, DelegatedAdminRelationshipRequest, ResourcePath("requests", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdminRelationship"
