from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class SortProperty(ClientValue):
    """Indicates the order to sort search results.

    Fields:
        isDescending (bool): True if the sort order is descending. Default is false,
             with the sort order as ascending. Optional.
        name (str): The name of the property to sort on. Required.
    """

    isDescending: bool | None = None
    name: str | None = None

    def __repr__(self):
        return f"{self.name} {'DESC' if self.isDescending else 'ASC'}"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SortProperty"
