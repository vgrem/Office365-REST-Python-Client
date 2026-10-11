from __future__ import annotations

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.audit.whois_history_record import WhoisHistoryRecord


class WhoisRecord(Entity):
    @property
    def history(self) -> EntityCollection[WhoisHistoryRecord]:
        """Gets the history property"""
        return self.properties.get(
            "history",
            EntityCollection[WhoisHistoryRecord](
                self.context, WhoisHistoryRecord, ResourcePath("history", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.WhoisRecord"
