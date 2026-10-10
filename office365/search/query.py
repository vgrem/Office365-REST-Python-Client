from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class SearchQuery(ClientValue):
    """
    Represents a search query that contains search terms and optional filters.

    Fields:
        queryString (str): The search query containing the search terms.
        queryTemplate (str): Provides a way to decorate the query string. Supports both KQL and query variables.
    """

    queryString: str | None = None
    queryTemplate: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchQuery"
