from __future__ import annotations

from dataclasses import dataclass

from office365.entity import Entity
from office365.runtime.client_value import ClientValue


@dataclass
class SearchHit(ClientValue):
    """
    Represents a single result within the list of search results.

    Fields:
        contentSource (str):
        summary (str): A summary of the result, if a summary is available.
        resource (Entity): The underlying Microsoft Graph representation of the search result.
        resultTemplateId (str): ID of the result template used to render the search result. This ID must map to
            a display layout in the resultTemplates dictionary that is also included in the searchResponse.
    """

    contentSource: str | None = None
    summary: str | None = None
    resource: Entity | None = None
    resultTemplateId: str | None = None

    hitId: str | None = None

    isCollapsed: bool | None = None

    rank: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchHit"
