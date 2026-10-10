from __future__ import annotations

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity


class Search(Entity):
    @property
    def entity_type_name(self):
        return "SP.Publishing.Search"

    @property
    def query_languages(self) -> ClientValueCollection:
        """Gets the QueryLanguages property"""
        return self.properties.get("QueryLanguages", ClientValueCollection(int))
