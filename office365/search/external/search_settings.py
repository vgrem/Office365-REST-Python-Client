from __future__ import annotations

from dataclasses import dataclass, field

from office365.externalconnectors.display_template import DisplayTemplate
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class SearchSettings(ClientValue):
    """Collects all configurable settings related to search over connector content."""

    searchResultTemplates: ClientValueCollection[DisplayTemplate] = field(
        default_factory=lambda: ClientValueCollection(DisplayTemplate)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.SearchSettings"
