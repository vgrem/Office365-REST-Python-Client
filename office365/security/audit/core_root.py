from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.security.audit.log_query import AuditLogQuery


class AuditCoreRoot(Entity):
    @property
    def queries(self) -> EntityCollection[AuditLogQuery]:
        """Gets the queries property"""
        from office365.security.audit.log_query import AuditLogQuery

        return self.properties.get(
            "queries",
            EntityCollection[AuditLogQuery](self.context, AuditLogQuery, ResourcePath("queries", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AuditCoreRoot"
