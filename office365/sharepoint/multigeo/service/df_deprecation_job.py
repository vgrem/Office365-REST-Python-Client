from __future__ import annotations

from typing_extensions import Self

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class DfDeprecationJob(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.MultiGeo.Service.DfDeprecationJob"

    def delete(self) -> Self:
        """Delete operation."""
        qry = ServiceOperationQuery(self, "Delete", None, {}, None, None)
        self.context.add_query(qry)
        return self
