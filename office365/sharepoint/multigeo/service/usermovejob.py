from __future__ import annotations

from datetime import datetime
from typing import Optional

from typing_extensions import Self

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class UserMoveJob(Entity):
    @property
    def is_content_moved(self) -> Optional[bool]:
        """Gets the IsContentMoved property"""
        return self.properties.get("IsContentMoved", None)

    @property
    def last_modified(self) -> Optional[datetime]:
        """Gets the LastModified property"""
        return self.properties.get("LastModified", None)

    @property
    def started_date_in_utc(self) -> Optional[datetime]:
        """Gets the StartedDateInUtc property"""
        return self.properties.get("StartedDateInUtc", None)

    @property
    def state_name(self) -> Optional[str]:
        """Gets the StateName property"""
        return self.properties.get("StateName", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.UserMoveJob"

    def cancel(self) -> Self:
        """Cancel operation."""
        qry = ServiceOperationQuery(self, "Cancel", None, {}, None, None)
        self.context.add_query(qry)
        return self
