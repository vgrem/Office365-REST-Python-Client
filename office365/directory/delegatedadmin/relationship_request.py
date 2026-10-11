from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.delegatedadmin.relationshiprequestaction import (
        DelegatedAdminRelationshipRequestAction,
    )
    from office365.directory.delegatedadmin.relationshiprequeststatus import (
        DelegatedAdminRelationshipRequestStatus,
    )


class DelegatedAdminRelationshipRequest(Entity):
    @property
    def action(self) -> DelegatedAdminRelationshipRequestAction:
        """Gets the action property"""
        from office365.directory.delegatedadmin.relationshiprequestaction import (
            DelegatedAdminRelationshipRequestAction,
        )

        return self.properties.get("action", DelegatedAdminRelationshipRequestAction.lockForApproval)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def status(self) -> DelegatedAdminRelationshipRequestStatus:
        """Gets the status property"""
        from office365.directory.delegatedadmin.relationshiprequeststatus import (
            DelegatedAdminRelationshipRequestStatus,
        )

        return self.properties.get("status", DelegatedAdminRelationshipRequestStatus.created)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdminRelationshipRequest"
