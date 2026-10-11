from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.delegatedadmin.access_container import (
        DelegatedAdminAccessContainer,
    )
    from office365.directory.delegatedadmin.access_details import (
        DelegatedAdminAccessDetails,
    )
    from office365.directory.delegatedadmin.accessassignmentstatus import (
        DelegatedAdminAccessAssignmentStatus,
    )


class DelegatedAdminAccessAssignment(Entity):
    @property
    def access_container(self) -> DelegatedAdminAccessContainer:
        """Gets the accessContainer property"""
        from office365.directory.delegatedadmin.access_container import (
            DelegatedAdminAccessContainer,
        )

        return self.properties.get("accessContainer", DelegatedAdminAccessContainer())

    @property
    def access_details(self) -> DelegatedAdminAccessDetails:
        """Gets the accessDetails property"""
        from office365.directory.delegatedadmin.access_details import (
            DelegatedAdminAccessDetails,
        )

        return self.properties.get("accessDetails", DelegatedAdminAccessDetails())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def status(self) -> DelegatedAdminAccessAssignmentStatus:
        """Gets the status property"""
        from office365.directory.delegatedadmin.accessassignmentstatus import (
            DelegatedAdminAccessAssignmentStatus,
        )

        return self.properties.get("status", DelegatedAdminAccessAssignmentStatus.pending)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdminAccessAssignment"
