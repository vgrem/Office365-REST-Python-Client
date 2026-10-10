from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ResourceReference(ClientValue):
    """Complex type containing properties of officeGraphInsights.

    Args:
        _id (str): The item's unique identifier.
        _type (str): A string value that can be used to classify the item, such as "microsoft.graph.driveItem"
        web_url (str): A URL leading to the referenced item.
    """

    id: str | None = None
    type: str | None = None
    webUrl: str | None = None

    def __str__(self):
        return self.type or ""

    def __repr__(self):
        return f"{self.type}:{self.webUrl}"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ResourceReference"
