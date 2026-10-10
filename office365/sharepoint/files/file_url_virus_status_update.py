from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class FileUrlVirusStatusUpdate(Entity):
    @property
    def file_url(self) -> Optional[str]:
        """Gets the fileUrl property"""
        return self.properties.get("fileUrl", None)

    @property
    def virus_message(self) -> Optional[str]:
        """Gets the virusMessage property"""
        return self.properties.get("virusMessage", None)

    @property
    def virus_status(self) -> bytes | None:
        """Gets the virusStatus property"""
        return self.properties.get("virusStatus", None)

    def update_virus_status(self) -> Self:
        """UpdateVirusStatus operation."""
        qry = ServiceOperationQuery(self, "UpdateVirusStatus", None, {}, None, None)
        self.context.add_query(qry)
        return self
